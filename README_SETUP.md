# Configuração de Credenciais Google Sheets

Para que este aplicativo funcione e possa ler/escrever na sua planilha, você precisa configurar uma **Service Account** no Google Cloud e compartilhar a planilha com ela.

## Passo 1: Criar Credenciais no Google Cloud

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto (ou selecione um existente).
3. No menu lateral, vá em **APIs e Serviços** > **Biblioteca**.
4. Pesquise e ative as seguintes APIs:
   - **Google Sheets API**
   - **Google Drive API**
5. Vá em **APIs e Serviços** > **Credenciais**.
6. Clique em **Criar Credenciais** > **Conta de serviço (Service Account)**.
7. Dê um nome para a conta (ex: `streamlit-sheets`) e clique em **Criar e Continuar**.
8. (Opcional) Dê permissão de "Editor" se quiser, mas não é estritamente necessário nesta etapa. Clique em **Concluir**.
9. Na lista de Contas de serviço, clique no email da conta que você acabou de criar (ex: `streamlit-sheets@seu-projeto.iam.gserviceaccount.com`).
10. Vá na aba **Chaves** > **Adicionar Chave** > **Criar nova chave**.
11. Escolha o formato **JSON** e clique em **Criar**.
12. Um arquivo será baixado para o seu computador. **Renomeie este arquivo para `credentials.json`**.

## Passo 2: Colocar o arquivo no projeto

Coloque o arquivo `credentials.json` na mesma pasta onde está o arquivo `app.py` (neste caso: `/home/ivan/Documentos/Fernando/Danilo Joan Evento/`).

## Passo 3: Compartilhar a Planilha

1. Abra a sua planilha no Google Sheets: [Link da Planilha](https://docs.google.com/spreadsheets/d/1U3YreWccWEyFfcUXlhOiLRzNUPsADoCFwuID8ruRWkk/edit?usp=sharing)
2. Clique no botão **Compartilhar** (Share) no canto superior direito.
3. Copie o **email da Service Account** (aquele que termina em `@...iam.gserviceaccount.com`) que está dentro do arquivo `credentials.json` (campo `client_email`).
4. Cole esse email na caixa de compartilhamento da planilha.
5. **Importante**: Dê permissão de **Editor** para que o app possa atualizar os dados (marcar presença, etc).
6. Clique em **Enviar** (Send).

## Passo 4: Rodar o App

Agora você pode rodar o aplicativo:

```bash
streamlit run app.py
```

Se tudo estiver correto, o app carregará os dados da planilha.
