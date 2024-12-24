def generate_response(text, target_language):
    try:
        if len(st.session_state.chat_history) == 0:
            # Add system initialization to chat history
            st.session_state.chat_history.append({"role": "system", "content": "You are Engli, an AI English trainer."})

        # Filter out assistant_translated messages for API call
        api_messages = [msg for msg in st.session_state.chat_history if msg["role"] != "assistant_translated"]
        api_messages.append({"role": "user", "content": text})

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=api_messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        assistant_response = completion.choices[0].message.content
        
        # Add messages to chat history
        st.session_state.chat_history.append({"role": "user", "content": text})
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Translate the assistant response to the target language
        translated_response = translate_text(assistant_response, target_language)
        # Store translation with special role (won't be used in API calls)
        st.session_state.chat_history.append({"role": "assistant_translated", "content": translated_response})

        return assistant_response, translated_response
    except Exception as e:
        st.error(f"Response generation failed: {e}")
        return "Sorry, I'm having trouble generating a response right now.", None
