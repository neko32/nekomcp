from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def main() -> None:
    llm = OllamaLLM(model = "llama3.1", temperature=1.0)
    template = """Question: {q}"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    # rez = chain.invoke({"q": "Question: Why cat is so cute? You need to tell me 5 reasons in Japanese man!"})
    #rez = chain.invoke({"q": "何故ねこちゃんはあんなにかわいいのか.. ５つ理由を教えて！"})
    #rez = chain.invoke({"q": "超戦闘プロレスFMWが裏千家の茶会を監修したらどんな感じになるかな？"})
    rez = chain.invoke({"q": "東京都の2番目の電波塔の名前は夢見櫓でなくスカイツリーが選ばれた。なぜ夢見櫓ではだめだったのか？怒りを込めて答えて！"})
    print(rez)


if __name__ == "__main__":
    main()