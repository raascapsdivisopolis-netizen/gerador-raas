import streamlit as st
import io
import json
from datetime import datetime

st.set_page_config(page_title="Gerador RAAS-PS", layout="wide")

st.title("🗂️ Gerador de Remessa RAAS-PS (DATASUS)")

if "atendimentos" not in st.session_state:
    st.session_state.atendimentos = []

# --- FUNÇÃO AUXILIAR PARA VALIDAR E CONVERTER DATAS DE DDMMAAAA PARA AAAAMMDD ---
def converter_data_para_sigtap(data_str):
    """
    Recebe uma string em formato DDMMAAAA (ex: 12082026) ou DDMMAA (ex: 120826) 
    e converte para AAAAMMDD (ex: 20260812).
    Remove barras ou caracteres inválidos automaticamente.
    Retorna None se a data for inválida.
    """
    limpa = ''.join(filter(str.isdigit, data_str))
    
    if len(limpa) == 8: # DDMMAAAA
        dia = limpa[0:2]
        mes = limpa[2:4]
        ano = limpa[4:8]
    elif len(limpa) == 6: # DDMMAA (Assume século 2000)
        dia = limpa[0:2]
        mes = limpa[2:4]
        ano = "20" + limpa[4:6]
    else:
        return None
        
    try:
        # Testa se a data é real (ex: evita 31/02)
        dt_obj = datetime(int(ano), int(mes), int(dia))
        return dt_obj.strftime("%Y%m%d") # Retorna AAAAMMDD
    except ValueError:
        return None

# --- CADASTRO INTELIGENTE DE PROFISSIONAIS ---
CADASTRO_PROFISSIONAIS = {
    "Selecione o Profissional...": {"cns": "000000000000000", "cbo": "000000"},
    "SUELY DE JESUS SILVA": {"cns": "701006885473793", "cbo": "239415"},
    "MANOELZITO VIEIRA SANTOS": {"cns": "703206632234698", "cbo": "791115"},
    "JUCELIA DE JESUS NERES": {"cns": "898005177012184", "cbo": "239410"},
    "JOYCE SOUZA SANTOS": {"cns": "700004226595607", "cbo": "251605"},
    "EVERALDO PRADO RODRIGUES SANTIAGO": {"cns": "705002815360557", "cbo": "225133"},
    "EDILSON DE JESUS SANTOS": {"cns": "700206945983830", "cbo": "251510"},
    "CLEYTON NUNES CAMPOS": {"cns": "709805043226294", "cbo": "223505"},
    "ALINE ALVES DE OLIVEIRA": {"cns": "708101591625938", "cbo": "422105"},
    "ALANE DE OLIVEIRA MACEDO": {"cns": "700609921575863", "cbo": "322205"},
}

# --- SISTEMA DE LOGIN SIMPLES ---
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    st.markdown("<h2 style='text-align: center; color: #2e6c80;'>🔐 Acesso Restrito - RAAS-PS Divisópolis</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit_login = st.form_submit_button("Entrar no Sistema", type="primary")
            
            if submit_login:
                if usuario == "digitador" and senha == "raas2026":
                    st.session_state.autenticado = True
                    st.rerun()
                elif usuario == "admin" and senha == "admindivisopolis":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
    return False

if not verificar_senha():
    st.stop()

# --- BOTÃO DE SAIR (LOGOUT) NA BARRA LATERAL ---
with st.sidebar:
    st.write("👤 **Sessão Ativa**")
    if st.button("🚪 Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()

# ==========================================
# INÍCIO DO SISTEMA RAAS-PS
# ==========================================

st.markdown("### ⚙️ Competência & Gerenciamento de Lote")
col_comp1, col_comp2, col_comp3 = st.columns([1, 1.5, 1.5])

with col_comp1:
    competencia_input = st.text_input("Competência Ativa (AAAAMM)", "202608")

with col_comp2:
    if len(st.session_state.atendimentos) > 0:
        json_str = json.dumps(st.session_state.atendimentos, ensure_ascii=False, indent=4)
        st.download_button(
            label="💾 Salvar Rascunho (Backup)",
            data=json_str,
            file_name=f"rascunho_raas_{competencia_input}.json",
            mime="application/json"
        )

with col_comp3:
    uploaded_backup = st.file_uploader("📂 Carregar Rascunho Salvo", type=["json"])
    if uploaded_backup is not None:
        try:
            dados_carregados = json.load(uploaded_backup)
            if isinstance(dados_carregados, list):
                st.session_state.atendimentos = dados_carregados
                st.success("Rascunho carregado com sucesso!")
        except Exception:
            st.error("Erro ao carregar backup.")

st.markdown("---")

col_form, col_hist = st.columns([1.3, 1])

with col_form:
    st.subheader("📝 Formulário de Digitação (Datas em DDMMAAAA)")
    
    with st.form("form_registro", clear_on_submit=False):
        tab_p, tab_a, tab_r = st.tabs(["[ P ] Paciente", "[ A ] Atendimento", "[ R ] Procedimento"])
        
        with tab_p:
            cnes = st.text_input("CNES Executante", "2119811", max_chars=7)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                prontuario = st.text_input("Prontuário", "0000000001", max_chars=10)
            with col2:
                cpf_user = st.text_input("CPF do Paciente (11 dígitos)", "06914796661", max_chars=11)
            with col3:
                cns_user = st.text_input("CNS do Paciente (ou Zeros)", "000000000000000", max_chars=15)
                
            col4, col5, col6 = st.columns(3)
            with col4:
                nome_user = st.text_input("Nome do Paciente", "ISMAEL CESAR")
            with col5:
                sexo = st.selectbox("Sexo", ["M", "F"])
            with col6:
                dt_nasc = st.text_input("Data Nascimento (DDMMAAAA - ex: 07091985)", "07091985", max_chars=10)
                
            col7, col8 = st.columns(2)
            with col7:
                raca_opt = st.selectbox("Raça/Cor", ["01 - Branca", "02 - Preta", "03 - Parda", "04 - Amarela", "05 - Indígena"], index=3)
            with col8:
                etnia = st.text_input("Etnia (4 dígitos)", "0000", max_chars=4)
                
            col9, col10 = st.columns(2)
            with col9:
                nome_mae = st.text_input("Nome da Mãe", "NELIA MARIA")
            with col10:
                nome_resp = st.text_input("Nome do Responsável", "APOLINARIO BORGES")
                
            st.markdown("##### Endereço")
            col11, col12, col13 = st.columns(3)
            with col11:
                cep = st.text_input("CEP", "39912000", max_chars=8)
            with col12:
                municipio = st.text_input("Município IBGE (c/ DV)", "3122450", max_chars=7)
            with col13:
                bairro = st.text_input("Bairro", "CENTRO")
                
            col14, col15, col16 = st.columns(3)
            with col14:
                tipo_log = st.text_input("Cód. Tipo Logradouro (3 dígitos)", "081", max_chars=3)
            with col15:
                logradouro = st.text_input("Nome Logradouro", "RUA JOSE FERRAZ")
            with col16:
                numero = st.text_input("Número", "00064", max_chars=5)
                
            col17, col18, col19, col20 = st.columns(4)
            with col17:
                complemento = st.text_input("Complemento", "CASA")
            with col18:
                tel_cel = st.text_input("Tel. Celular (11 dígitos)", "39912000312", max_chars=11)
            with col19:
                tel_contato = st.text_input("Tel. Contato (11 dígitos)", "99999999999", max_chars=11)
            with col20:
                situacao_rua = st.selectbox("Em Situação de Rua?", ["N", "S"], index=0)

        with tab_a:
            col21, col22, col22b = st.columns(3)
            with col21:
                dt_admissao = st.text_input("Data Admissão (DDMMAAAA - ex: 12082026)", "12082026", max_chars=10)
            with col22:
                carater_opt = st.selectbox("Caráter Atendimento", ["01 - Eletivo", "02 - Urgência"], index=0)
            with col22b:
                origem_opt = st.selectbox("Origem do Usuário", ["01 - Demanda Espontânea", "02 - Atenção Básica", "03 - Urgência", "04 - Outro CAPS"], index=0)
                
            col23, col24 = st.columns(2)
            with col23:
                cid_principal = st.text_input("CID Principal (Ex: F411)", "F411", max_chars=4)
            with col24:
                cid_associado = st.text_input("CID Associado (Opcional)", "", max_chars=4)
                
            st.markdown("##### Usuário de Álcool/Drogas")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                usu_droga = st.selectbox("Usuário de Drogas?", ["N", "S"], index=0)
            with col_d2:
                tipo_droga_opt = st.multiselect("Tipos", ["Álcool", "Crack", "Outras"])

            st.markdown("##### Cobertura ESF")
            col25, col26 = st.columns(2)
            with col25:
                cobertura_esf = st.selectbox("Cobertura ESF?", ["N", "S"], index=1)
            with col26:
                cnes_esf = st.text_input("CNES USF (Se ESF=S)", "2119811", max_chars=7)
                
            col27, col28 = st.columns(2)
            with col27:
                destino_opt = st.selectbox("Destino Usuário", ["00 - Permanência", "01 - Continuidade Outro CAPS", "02 - Continuidade AB", "03 - Alta"], index=0)
            with col28:
                dt_conclusao = st.text_input("Data Alta/Conclusão (DDMMAAAA - Opcional)", "", max_chars=10)

        with tab_r:
            st.markdown("##### Selecione o Profissional")
            prof_selecionado = st.selectbox(
                "Profissional Executante", 
                list(CADASTRO_PROFISSIONAIS.keys()),
                key="select_profissional"
            )
            
            dados_prof = CADASTRO_PROFISSIONAIS.get(prof_selecionado, {"cns": "000000000000000", "cbo": "000000"})
            
            col29, col30 = st.columns(2)
            with col29:
                dt_atend = st.text_input("Data do Procedimento (DDMMAAAA - ex: 12082026)", "12082026", max_chars=10)
            with col30:
                procedimento = st.text_input("Procedimento SIGTAP (10 dígitos)", "0301080020", max_chars=10)
                
            col31, col32, col33 = st.columns(3)
            with col31:
                quantidade = st.text_input("Quantidade", "2", max_chars=6)
            with col32:
                servico = st.text_input("Serviço (3 dígitos)", "115", max_chars=3)
            with col33:
                classificacao = st.text_input("Classificação (3 dígitos)", "001", max_chars=3)
                
            col34, col35, col36 = st.columns(3)
            with col34:
                cns_prof = st.text_input("CNS Profissional", value=dados_prof["cns"], max_chars=15, key="input_cns_prof")
            with col35:
                cbo = st.text_input("CBO Profissional", value=dados_prof["cbo"], max_chars=6, key="input_cbo_prof")
            with col36:
                local_realizacao = st.selectbox("Local Realização", ["C - CAPS", "T - Território"], index=0)

            submitted = st.form_submit_button("➕ Adicionar Lançamento ao Lote", type="primary")

        if submitted:
            cpf_limpo = ''.join(filter(str.isdigit, cpf_user)).zfill(11)
            
            # Validação das datas convertidas de DDMMAAAA para AAAAMMDD
            dt_nasc_conv = converter_data_para_sigtap(dt_nasc)
            dt_admissao_conv = converter_data_para_sigtap(dt_admissao)
            dt_atend_conv = converter_data_para_sigtap(dt_atend)
            dt_conclusao_conv = converter_data_para_sigtap(dt_conclusao) if dt_conclusao.strip() else "".ljust(8, ' ')

            if len(cpf_limpo) != 11 or cpf_limpo == "00000000000":
                st.error("Informe um CPF válido com 11 dígitos!")
            elif not nome_user or not nome_mae:
                st.error("Nome do Paciente e Nome da Mãe são obrigatórios!")
            elif not dt_nasc_conv:
                st.error("Data de Nascimento inválida! Use o formato DDMMAAAA (ex: 07091985).")
            elif not dt_admissao_conv:
                st.error("Data de Admissão inválida! Use o formato DDMMAAAA (ex: 12082026).")
            elif not dt_atend_conv:
                st.error("Data do Procedimento inválida! Use o formato DDMMAAAA (ex: 12082026).")
            elif dt_conclusao.strip() and not dt_conclusao_conv:
                st.error("Data de Conclusão/Alta inválida! Use o formato DDMMAAAA.")
            elif len(cid_principal.strip()) < 4:
                st.error("O CID Principal deve ter 4 caracteres (Ex: F411)!")
            else:
                str_droga = ""
                if usu_droga == "S":
                    if "Álcool" in tipo_droga_opt: str_droga += "A"
                    if "Crack" in tipo_droga_opt: str_droga += "C"
                    if "Outras" in tipo_droga_opt: str_droga += "O"
                str_droga = str_droga.ljust(3, ' ')[:3]
                
                novo_registro = {
                    "cnes": cnes.zfill(7), "prontuario": prontuario.zfill(10), "cpf_user": cpf_limpo,
                    "cns_user": cns_user.zfill(15), "nome_user": nome_user.strip().upper(), "sexo": sexo,
                    "dt_nasc": dt_nasc_conv, "raca": raca_opt[:2], "etnia": etnia.zfill(4),
                    "nome_mae": nome_mae.strip().upper(), "nome_resp": (nome_resp.strip().upper() if nome_resp else nome_mae.strip().upper()),
                    "cep": cep.zfill(8), "municipio": municipio.zfill(7), "bairro": bairro.strip().upper().ljust(30, ' ')[:30],
                    "tipo_log": tipo_log.zfill(3), "logradouro": logradouro.strip().upper().ljust(30, ' ')[:30],
                    "numero": numero.zfill(5), "complemento": complemento.strip().upper().ljust(10, ' ')[:10],
                    "tel_cel": tel_cel.zfill(11), "tel_contato": tel_contato.zfill(11),
                    "situacao_rua": situacao_rua, "dt_admissao": dt_admissao_conv,
                    "carater_atend": carater_opt[:2], "origem_usuario": origem_opt[:2],
                    "cid_principal": cid_principal.strip().upper().ljust(4, ' ')[:4],
                    "cid_associado": cid_associado.strip().upper().ljust(4, ' ')[:4] if cid_associado else "".ljust(4, ' '),
                    "usu_droga": usu_droga, "tipo_droga": str_droga,
                    "cobertura_esf": cobertura_esf, "cnes_esf": cnes_esf.zfill(7) if cobertura_esf == "S" else "0".zfill(7),
                    "destino_usuario": destino_opt[:2], "dt_conclusao": dt_conclusao_conv,
                    "dt_atend": dt_atend_conv, "procedimento": procedimento.zfill(10),
                    "quantidade": quantidade.zfill(6), "servico": servico.zfill(3),
                    "classificacao": classificacao.zfill(3), "cns_prof": dados_prof["cns"].zfill(15),
                    "cbo": dados_prof["cbo"].zfill(6), "local_realizacao": local_realizacao[0]
                }
                st.session_state.atendimentos.append(novo_registro)
                st.success(f"Atendimento de {novo_registro['nome_user']} adicionado!")

with col_hist:
    st.subheader("📋 Histórico do Lote Atual")
    
    cpfs_unicos = set(reg['cpf_user'] for reg in st.session_state.atendimentos)
    total_pacientes = len(cpfs_unicos)
    total_registros_brutos = len(st.session_state.atendimentos)
    
    st.metric(label="Total de Pacientes no Lote", value=total_pacientes)
    if total_registros_brutos > total_pacientes:
        st.caption(f"*(Total de {total_registros_brutos} ações/procedimentos registrados)*")
    
    if total_registros_brutos == 0:
        st.info("Nenhum atendimento adicionado ainda.")
    else:
        ultimos = list(enumerate(st.session_state.atendimentos))[-20:][::-1]
        for idx, reg in ultimos:
            with st.expander(f"👤 {reg['nome_user']} (CPF: {reg['cpf_user']})"):
                st.write(f"**Procedimento:** {reg['procedimento']} | **Data:** {reg['dt_atend']}")
                st.write(f"**CID:** {reg['cid_principal']} | **Mãe:** {reg['nome_mae']}")
                if st.button("🗑️ Excluir este lançamento", key=f"del_{idx}"):
                    st.session_state.atendimentos.pop(idx)
                    st.rerun()

    st.markdown("---")
    if total_registros_brutos > 0:
        if st.button("💾 Gerar e Baixar Arquivo Oficial (AA312245)", type="primary"):
            ano_mes = competencia_input.strip()
            codigo_uf = "31"
            data_geracao = "20261012"
            
            linhas_detalhe = []
            sub16_total = 0
            sub15_total = 0
            
            for reg in st.session_state.atendimentos:
                sub16_total += int(reg["procedimento"]) + int(reg["quantidade"])
                sub15_total += int(reg["cnes"]) + int(int(reg["cpf_user"]) if reg["cpf_user"].isdigit() else 0)
                
                linha15 = (
                    "15" + codigo_uf + ano_mes + reg["cnes"] + reg["cns_user"] + reg["dt_admissao"] + 
                    "".ljust(8, ' ') + reg["nome_user"].ljust(30, ' ')[:30] + reg["prontuario"] + 
                    reg["nome_mae"].ljust(30, ' ')[:30] + reg["logradouro"] + reg["numero"] + 
                    reg["complemento"] + reg["cep"] + reg["municipio"] + reg["dt_nasc"] + 
                    reg["sexo"] + reg["raca"] + reg["nome_resp"].ljust(30, ' ')[:30] + 
                    "010" + reg["etnia"] + reg["tel_contato"] + reg["tel_cel"] + 
                    reg["destino_usuario"] + reg["dt_conclusao"] + reg["cid_principal"] + 
                    "".ljust(4, ' ') + "".ljust(4, ' ') + "".ljust(4, ' ') + reg["cid_associado"] + 
                    reg["carater_atend"] + reg["origem_usuario"] + reg["cobertura_esf"] + 
                    reg["cnes_esf"] + "00001" + reg["destino_usuario"] + "RAS" + reg["situacao_rua"] + 
                    reg["usu_droga"] + reg["tipo_droga"] + "".ljust(13, ' ') + reg["bairro"] + 
                    reg["tipo_log"] + "".ljust(40, ' ') + reg["cpf_user"] + "".ljust(4, ' ')
                )
                
                linha16 = (
                    "16" + codigo_uf + ano_mes + reg["cnes"] + reg["cns_user"] + reg["dt_admissao"] + 
                    reg["procedimento"] + reg["cbo"] + reg["cns_prof"] + reg["dt_atend"] + 
                    reg["servico"] + reg["classificacao"] + reg["quantidade"] + "RAS" + 
                    reg["local_realizacao"] + reg["cpf_user"] + "".ljust(4, ' ')
                )
                
                linhas_detalhe.append(linha15)
                linhas_detalhe.append(linha16)
            
            soma_ctrl = str(1111 + ((sub16_total + sub15_total) % 1111)).zfill(4)
            qtd_folhas_str = str(total_registros_brutos).zfill(6)
            sufixo_comp_b = f"{ano_mes}b"
            
            cabecalho = (
                "01" + "#RAS#" + ano_mes + qtd_folhas_str + soma_ctrl + 
                "SMS DIVISOPOLIS               ".ljust(30, ' ') + 
                "SMS   ".ljust(6, ' ') + "66234311000123".zfill(14) + 
                "SMS DIVISOPOLIS                         ".ljust(40, ' ') + 
                "M" + data_geracao + "02.35          " + sufixo_comp_b
            )
            
            conteudo_final = cabecalho + "\r\n" + "\r\n".join(linhas_detalhe) + "\r\n"
            b_io = io.BytesIO(conteudo_final.encode("cp1252", errors="ignore"))
            
            st.success("Remessa gerada com sucesso!")
            st.download_button(
                label="📥 Baixar Arquivo Remessa AA312245",
                data=b_io,
                file_name="AA312245",
                mime="application/octet-stream"
            )
