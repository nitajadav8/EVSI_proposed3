from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="sk_vzs6qle8_3WnCHGCgtx37kvOTXQEOtArC",
)

response = client.text.translate(
    input="Hi, My Name is Vinayak.",
    source_language_code="auto",
    target_language_code="gu-IN",
    speaker_gender="Male"
)

print(response)
