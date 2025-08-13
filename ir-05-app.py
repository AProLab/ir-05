import streamlit as st
import requests
import base64


class EnglishToKoreanTranslator:
    """영어 문장 이미지를 인식해 한국어로 번역하는 클래스"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def _encode_image(self, file_image):
        """이미지를 base64로 인코딩"""
        file_image.seek(0)
        image_bytes = file_image.read()
        return base64.b64encode(image_bytes).decode("utf-8")

    def _build_prompt(self, base64_image: str):
        """API 요청 메시지 생성"""
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                            입력된 사진 속 영어문장을 인식하고, [출력 예1] 형식과 같이 자연스러운 한글로 번역해주세요.

                            [출력 예 1]
                            **:red[[원문]]**: [인식된 영어 문장 출력]
                            **:blue[[번역]]**: [한글 번역 결과 출력]

                            입력된 사진으로 영어 문장을 인식할 수 없거나, 관련 없는 사진일 경우 [출력 예 2]와 같이 출력하세요

                            [출력 예 2]
                            **죄송합니다. 인식할 수 없는 사진입니다.**
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]

    def translate(self, file_image):
        """이미지에서 영어 문장을 인식하고 한글로 번역"""
        base64_image = self._encode_image(file_image)
        messages = self._build_prompt(base64_image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": messages
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


class EnglishToKoreanApp:
    """영어 번역 Streamlit UI 클래스"""
    def __init__(self):
        self.api_key = None
        self.file_image_english = None

    def run(self):
        """Streamlit 앱 실행"""
        st.header("영어 문장 → 한글 번역")
        self.api_key = st.text_input("OPENAI API KEY를 입력하세요.", type="password")
        self.file_image_english = st.file_uploader("영어 문장 사진만 업로드하세요!", type=['png', 'jpg', 'jpeg'])

        if self.api_key and self.file_image_english:
            translator = EnglishToKoreanTranslator(self.api_key)
            st.image(self.file_image_english, width=500)

            with st.spinner("한글로 번역중..."):
                try:
                    result = translator.translate(self.file_image_english)
                    st.markdown(result)
                except requests.exceptions.RequestException as e:
                    st.error(f"API 요청 오류: {e}")


if __name__ == "__main__":
    app = EnglishToKoreanApp()
    app.run()