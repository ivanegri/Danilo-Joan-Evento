import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import time
st.set_page_config(
    page_title="Gestão de Eventos",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: black;
    }
    .metric-card h3, .metric-card h2 {
        color: black !important;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Escopos para API do Google
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def authenticate_google_sheets():
    """Autentica usando st.secrets do Streamlit (funciona em produção e localmente)"""
    try:
        # Verifica se a secret existe
        if "gcp_service_account" not in st.secrets:
            st.error("❌ Secret 'gcp_service_account' não encontrada")
            st.info("""
            **Para Streamlit Cloud:**
            1. Acesse https://share.streamlit.io/
            2. Clique em sua app → Settings → Secrets
            3. Cole o seguinte (substitua pelos valores reais):
            ```toml
            [gcp_service_account]
            type = "service_account"
            project_id = "seu_project_id"
            private_key_id = "sua_chave_id"
            private_key = "sua_chave_privada"
            client_email = "seu_email"
            client_id = "seu_client_id"
            auth_uri = "https://accounts.google.com/o/oauth2/auth"
            token_uri = "https://oauth2.googleapis.com/token"
            auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
            client_x509_cert_url = "seu_cert_url"
            universe_domain = "googleapis.com"
            ```
            """)
            return None
        
        # Carrega as credenciais
        service_account_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        return gspread.authorize(creds)
        
    except Exception as e:
        st.error(f"❌ Erro ao autenticar: {str(e)}")
        return None

def get_data(client, sheet_identifier):
    try:
        if sheet_identifier.startswith("https://"):
            sheet = client.open_by_url(sheet_identifier).sheet1
        else:
            sheet = client.open(sheet_identifier).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df, sheet
    except Exception as e:
        st.error(f"Erro ao acessar a planilha: {e}")
        return None, None

def main():
    st.title("📅 Gestão de Presença em Eventos")
    st.markdown("---")

    # Sidebar para Configuração
    # Sidebar Simplificada
    with st.sidebar:
        st.header("⚙️ Configuração")
        
        client = authenticate_google_sheets()
        
        if not client:
            st.error("❌ Falha na autenticação com Google Sheets.")
            st.info("Verifique se o arquivo `.streamlit/secrets.toml` está corretamente configurado com as credenciais do Google Cloud.")
            return

        st.success("✅ Conectado ao Google Drive")
        st.markdown("---")
        
        sheet_url = st.text_input("URL da Planilha", value="https://docs.google.com/spreadsheets/d/1U3YreWccWEyFfcUXlhOiLRzNUPsADoCFwuID8ruRWkk/edit?usp=sharing")
        
        if st.button("🔄 Recarregar Dados"):
            st.rerun()

    # Área Principal
    if sheet_url:
        df, sheet = get_data(client, sheet_url)
        
        if df is not None:
            # Identificar colunas importantes
            attendance_col = next((col for col in ['Comparecimento', 'Compareceu', 'Presença Confirmada'] if col in df.columns), 'Comparecimento')
            
            # Métricas Rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><h3>Total Convidados</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            with col2:
                confirmados = len(df[df['Presença'].astype(str).str.lower() == 'sim']) if 'Presença' in df.columns else 0
                st.markdown(f"<div class='metric-card'><h3>Confirmados (RSVP)</h3><h2>{confirmados}</h2></div>", unsafe_allow_html=True)
            with col3:
                presentes = 0
                if attendance_col in df.columns:
                    presentes = len(df[df[attendance_col].astype(str).str.lower().isin(['ok', 'sim', 'true'])])
                st.markdown(f"<div class='metric-card'><h3>Compareceram</h3><h2>{presentes}</h2></div>", unsafe_allow_html=True)

            st.markdown("### 🔍 Filtros e Busca")
            
            col_search, col_city = st.columns(2)
            
            with col_search:
                search_term = st.text_input("Buscar por Nome", placeholder="Digite o nome...")
            
            with col_city:
                cities = df['Cidade'].unique().tolist() if 'Cidade' in df.columns else []
                selected_city = st.selectbox("Filtrar por Cidade", ["Todas"] + cities)

            # Aplicar Filtros
            filtered_df = df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['Nome'].astype(str).str.contains(search_term, case=False, na=False)]
            if selected_city != "Todas":
                filtered_df = filtered_df[filtered_df['Cidade'] == selected_city]

            # Mostrar apenas Nome e Cidade na tabela principal
            display_cols = [col for col in ['Nome', 'Cidade'] if col in filtered_df.columns]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### ✏️ Atualizar Registro")

            # Seleção de convidado para edição
            # Criar uma lista de nomes para o selectbox baseada no filtro atual
            guest_options = filtered_df['Nome'].tolist() if 'Nome' in filtered_df.columns else []
            
            if guest_options:
                selected_guest_name = st.selectbox("Selecione um Convidado para editar", guest_options)
                
                # Pegar dados do convidado selecionado
                guest_data = df[df['Nome'] == selected_guest_name].iloc[0]
                
                st.markdown("### ✏️ Editar Convidado")
                
                with st.container(border=True):
                    st.markdown(f"**Editando:** `{selected_guest_name}`")
                    
                    with st.form("update_form", border=False):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        
                        with c1:
                            new_phone = st.text_input("📱 Telefone", value=str(guest_data.get('Telefone', '')), placeholder="(00)99999-9999", help="Digite no formato (DD)99999-9999")
                        
                        with c2:
                            st.markdown("**RSVP (Confirmado?)**")
                            confirm_presence = st.toggle("Sim, confirmado", value=(str(guest_data.get('Presença', '')).lower() == 'sim'))
                        
                        with c3:
                            st.markdown("**Check-in (Compareceu?)**")
                            # Lógica para checkbox de comparecimento
                            current_att_val = str(guest_data.get(attendance_col, '')).lower()
                            is_attended = current_att_val in ['ok', 'sim', 'true']
                            mark_attended = st.toggle("Sim, presente", value=is_attended)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        submit_button = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)

                    if submit_button:
                        try:
                            # Encontrar a célula pelo Nome para garantir a linha correta
                            try:
                                cell = sheet.find(selected_guest_name)
                                row_number = cell.row
                            except gspread.exceptions.CellNotFound:
                                st.error(f"Não foi possível encontrar o nome '{selected_guest_name}' na planilha original.")
                                st.stop()
                            
                            headers = df.columns.tolist()
                            
                            # Atualizar Telefone
                            if 'Telefone' in headers:
                                col_idx = headers.index('Telefone') + 1
                                sheet.update_cell(row_number, col_idx, new_phone)
                            
                            # Atualizar Presença (RSVP)
                            if 'Presença' in headers:
                                col_idx = headers.index('Presença') + 1
                                sheet.update_cell(row_number, col_idx, 'Sim' if confirm_presence else 'Não')
                                
                            # Atualizar Comparecimento
                            if attendance_col in headers:
                                col_idx = headers.index(attendance_col) + 1
                                sheet.update_cell(row_number, col_idx, 'Ok' if mark_attended else '')
                            else:
                                st.warning(f"A coluna '{attendance_col}' não existe na planilha. Adicione-a manualmente.")

                            st.success(f"Dados de {selected_guest_name} atualizados com sucesso!")
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {e}")
            else:
                st.info("Nenhum convidado encontrado com os filtros atuais.")
        else:
            st.warning("Não foi possível carregar os dados. Verifique o nome da planilha e as permissões.")
            st.markdown("""
            **Certifique-se que:**
            1. A planilha existe no Google Drive.
            2. Você compartilhou a planilha com o email da Service Account (presente no `credentials.json`).
            3. A planilha tem as colunas: `Nome`, `Cidade`, `Telefone`, `Presença`, `Compareceu`.
            """)

if __name__ == "__main__":
    main()
