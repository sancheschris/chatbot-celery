from google.genai import types


class GeminiMessageAdapter:
    @staticmethod
    def build(messages):
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list of dictionaries.")
        
        system_messages = []
        contents = []

        for message in messages:
            if not isinstance(message, dict):
                raise ValueError("Each message must be a dictionary.")
        
        role = message.get("role")
        text = message.get("text")

        if not role or text is None:
            raise ValueError("Each message must have a 'role' and 'text' field.")
        
        if not isinstance(text, str):
            raise ValueError("The 'text' field must be a string.")
        
        if role == "system":
            system_messages.append(text)
        
        elif role == "user":
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text)],
                )
            )
        
        elif role == "assistant":
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text)],
                )
            )

        else:
            raise ValueError(f"Unsupported role: {role}")
        
        config = None
        if system_messages:
            config = types.GenerateContentConfig(
                system_instruction="\n".join(system_messages)
            )
        return contents, config
        