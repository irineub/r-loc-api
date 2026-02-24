# Servidor de Uploads Ngrok para Desenvolvimento

Para facilitar o desenvolvimento com a UazAPI e testar envios de PDFs via WhatsApp em localhost, criei este utilitário. A UazAPI requer uma URL de documento publicamente acessível para baixar as faturas/recibos, e em localhost isso não é possível.

Assim, rodamos um servidor estático extra para o diretório `/uploads` via FastAPI na porta 8030 que em seguida será exposto globalmente pelo `ngrok`.

## Usando o Ngrok Local

1. Instale o Ngrok caso ainda não possua e configure ele globalmente ou via binário `ngrok`.

   ```bash
   npm i ngrok -g
   # Ou faça o download oficial e mova para os seus binaries locais
   ```

2. Adicione sua conta ngrok via token do painel (https://dashboard.ngrok.com/get-started/your-authtoken)

   ```bash
   ngrok config add-authtoken <TOKEN>
   ```

3. Em um terminal paralelo ative seu venv Python e inicie o mini-webserver que servirá a pasta:

   ```bash
   cd ./r-loc-api
   source venv/bin/activate
   # Porta padrão = 8030
   python uploads-server-ngrok/ngrok_fastapi_uploads.py
   ```

4. Em outro terminal, rode o ngrok para gerar o túnel externo associado à porta 8030:
   
   ```bash
   ngrok http 8030
   ```

5. Copie a URL gerada (ex: `https://abcd-123-45...ngrok-free.app`)

6. No Front-End (R-Loc), abra o menu **Config**
   - Habilite "Habilitar Ngrok Local"
   - Cole o link `https://abcd-123...ngrok-free.app` na "URL do Servidor Ngrok"
   - Salve as configurações
   
Sempre que um PDF for gerado ou algum upload local que precise de acesso publico web acontecer, a url do tunel Ngrok substitui a base `request.base_url` para servir o PDF e mandar para API do whatsapp.
