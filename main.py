import os
from datetime import datetime

import requests
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(
    title="Exchange API",
    version="1.0.0",
    description="Converte valores entre duas moedas usando uma fonte externa (AwesomeAPI)."
)

# URL da API de câmbio externa
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://economia.awesomeapi.com.br/last")


@app.get("/exchange/{from_currency}/{to_currency}")
def convert_currency(from_currency: str, to_currency: str, request: Request):
    # Verifica se o header com o ID da conta está presente (injetado pelo gateway)
    account_id = request.headers.get("id-account")
    if not account_id:
        raise HTTPException(status_code=401, detail="Missing id-account header")

    # Ex: USD-BRL
    pair = f"{from_currency.upper()}-{to_currency.upper()}"

    try:
        response = requests.get(f"{EXTERNAL_API_URL}/{pair}", timeout=5)
        response.raise_for_status()
        data = response.json()
        key = f"{from_currency.upper()}{to_currency.upper()}"
        quote = data[key]
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Erro ao consultar a API externa de câmbio."
        ) from exc

    return {
        "sell": float(quote["ask"]),
        "buy": float(quote["bid"]),
        "date": datetime.fromtimestamp(int(quote["timestamp"])).strftime("%Y-%m-%d %H:%M:%S"),
        "id-account": account_id
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000")) 
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
