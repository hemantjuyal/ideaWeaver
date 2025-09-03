import streamlit as st
import logging
import json

def render_ui(api_client):
    st.title("🤖 Idea Weaver")

    # Initialize session state variables if they don't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.collected_inputs = {}
        st.session_state.master_agent_finished = False
        st.session_state.last_question = None

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initial prompt from the master agent if the conversation has just started
    if not st.session_state.messages:
        with st.spinner("Initializing conversation..."):
            initial_response_data = api_client.call_master_agent_api(
                conversation_history="",
                user_input="",
                collected_inputs={},
                last_question=st.session_state.last_question
            )
            if initial_response_data.get("status") == "continue":
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": initial_response_data.get("message", "")
                })
                st.session_state.conversation_history.append(
                    f"Assistant: {initial_response_data.get('message', '')}"
                )
                st.session_state.last_question = initial_response_data.get("last_question")
                st.rerun()  # Rerun to display the initial message
            else:
                st.error("An unexpected error occurred during initialization. Please try again.")
                st.stop()

    # Handle user input
    if not st.session_state.master_agent_finished:
        if user_input := st.chat_input("Your response:", key="user_input_chat"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.conversation_history.append(f"User: {user_input}")
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)

            # Get assistant response
            with st.spinner("Thinking..."):
                collected_inputs = st.session_state.collected_inputs
                logging.info(f"Sending collected_inputs to backend: {json.dumps(collected_inputs, indent=2)}")

                assistant_response_data = api_client.call_master_agent_api(
                    conversation_history="\n".join(st.session_state.conversation_history),
                    user_input=user_input,
                    collected_inputs=collected_inputs,
                    last_question=st.session_state.last_question
                )
                status = assistant_response_data.get("status")
                message = assistant_response_data.get("message")
                data = assistant_response_data.get("data", {})
                st.session_state.last_question = assistant_response_data.get("last_question")

                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(message)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": message})
                st.session_state.conversation_history.append(f"Assistant: {message}")
                st.session_state.collected_inputs = data or {}
                if status == "complete":
                    st.session_state.master_agent_finished = True
                
            st.rerun()  # Rerun to trigger the story generation

    # Trigger main story generation once master agent is finished
    if st.session_state.master_agent_finished:
        with st.chat_message("assistant"):
            st.markdown("I have all the information I need. I will now start weaving your story concept. This might take a moment...")
        with st.spinner("Weaving your story idea... Please wait."):
            response_data = api_client.call_generate_story_api(
                collected_inputs=st.session_state.collected_inputs
            )
            if response_data.get("status") == "complete":
                story_summary = response_data.get("data", {}).get("story_summary", "")
                st.session_state.messages.append({"role": "assistant", "content": response_data.get("message", "")})
                st.session_state.messages.append({"role": "assistant", "content": story_summary})
                with st.chat_message("assistant"):
                    st.markdown(response_data.get("message", ""))
                    st.markdown(story_summary)
            else:
                error_message = response_data.get("message", "An unexpected error occurred during story generation.")
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                with st.chat_message("assistant"):
                    st.markdown(error_message)

        st.session_state.master_agent_finished = False  # Reset to prevent re-running immediately
        st.session_state.messages.append({"role": "assistant", "content": "Story concept generated! Would you like to start a new story?"})
        st.session_state.conversation_history.append("Assistant: Story concept generated! Would you like to start a new story?")
        st.rerun()

    # End of conversation / Start new story button
    if st.session_state.master_agent_finished and st.session_state.messages[-1]["content"] == "Story concept generated! Would you like to start a new story?":
        st.button("Start a New Story", on_click=lambda: st.session_state.clear())
