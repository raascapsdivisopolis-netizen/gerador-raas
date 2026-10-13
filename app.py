import streamlit as st
import io
import json
from datetime import datetime

st.set_page_config(page_title="Gerador RAAS-PS", layout="wide")

st.title("🗂️ Gerador de Remessa RAAS-PS (DATASUS)")

if "atendimentos" not in st.session_state:
    st.session_state.atendimentos = []

# --- TABELA OFICIAL DE TIPOS DE LOGRADOURO ---
TABELA_TIPO_LOGRADOURO = {
    "Selecione o Tipo...": "",
    "081 - RUA": "081",
    "008 - AVENIDA": "008",
    "100 - TRAVESSA": "100",
    "037 - FAZENDA": "037",
    "828 - POVOADO": "828",
    "092 - SITIO": "092",
    "713 - COMUNIDADE": "713",
    "065 - PRACA": "065"
}

# --- FUNÇÃO AUXILIAR PARA VALIDAR E CONVERTER DATAS DE DDMMAAAA PARA AAAAMMDD ---
def converter_data_para_sigtap(data_str):
    limpa = ''.join(filter(str.isdigit, data_str))
    
    if len(limpa) == 8: # DDMMAAAA
        dia = limpa[0:2]
        mes = limpa[2:4]
        ano = limpa[4:8]
    elif len(limpa) == 6: # DDMMAA
        dia = limpa[0:2]
        mes = limpa[2:4]
        ano = "20" + limpa[4:6]
    else:
        return None
        
    try:
        dt_obj = datetime(int(ano), int(mes), int(dia))
        return dt_obj.strftime("%Y%m%d")
    except ValueError:
        return None

# --- CADASTRO INTELIGENTE DE PROFISSIONAIS ---
CADASTRO_PROFISSIONAIS = {
    "Selecione o Profissional...": {"cns": "", "cbo": ""},
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
    st.subheader("📝 Formulário de Digitação (Em Branco)")
    
    with st.form("form_registro", clear_on_submit=False):
        tab_p, tab_a, tab_r = st.tabs(["[ P ] Paciente", "[ A ] Atendimento", "[ R ] Procedimento"])
        
        with tab_p:
            # CNES atualizado para 7500238
            cnes = st.text_input("CNES Executante", "7500238", max_chars=7)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                prontuario = st.text_input("Prontuário", "", max_chars=10)
            with col2:
                cpf_user = st.text_input("CPF do Paciente (11 dígitos)", "", max_chars=11)
            with col3:
                cns_user = st.text_input("CNS do Paciente (ou Zeros)", "", max_chars=15)
                
            col4, col5, col6 = st.columns(3)
            with col4:
                nome_user = st.text_input("Nome do Paciente", "")
            with col5:
                sexo = st.selectbox("Sexo", ["", "M", "F"])
            with col6:
                dt_nasc = st.text_input("Data Nascimento (DDMMAAAA)", "", max_chars=10)
                
            col7, col8 = st.columns(2)
            with col7:
                raca_opt = st.selectbox("Raça/Cor", ["", "01 - Branca", "02 - Preta", "03 - Parda", "04 - Amarela", "05 - Indígena"])
            with col8:
                etnia = st.text_input("Etnia (4 dígitos)", "", max_chars=4)
                
            col9, col10 = st.columns(2)
            with col9:
                nome_mae = st.text_input("Nome da Mãe", "")
            with col10:
                nome_resp = st.text_input("Nome do Responsável", "")
                
            st.markdown("##### Endereço")
            col11, col12, col13 = st.columns(3)
            with col11:
                cep = st.text_input("CEP", "", max_chars=8)
            with col12:
                municipio = st.text_input("Município IBGE (c/ DV)", "", max_chars=7)
            with col13:
                bairro = st.text_input("Bairro", "")
                
            col14, col15, col16 = st.columns(3)
            with col14:
                tipo_log_selecionado = st.selectbox("Tipo de Logradouro", list(TABELA_TIPO_LOGRADOURO.keys()))
                codigo_tipo_log = TABELA_TIPO_LOGRADOURO[tipo_log_selecionado]
            with col15:
                logradouro = st.text_input("Nome Logradouro", "")
            with col16:
                numero = st.text_input("Número", "", max_chars=5)
                
            col17, col18, col19, col20 = st.columns(4)
            with col17:
                complemento = st.text_input("Complemento", "")
            with col18:
                tel_cel = st.text_input("Tel. Celular (11 dígitos)", "", max_chars=11)
            with col19:
                tel_contato = st.text_input("Tel. Contato (11 dígitos)", "", max_chars=11)
            with col20:
                situacao_rua = st.selectbox("Em Situação de Rua?", ["", "N", "S"])

        with tab_a:
            col21, col22, col22b = st.columns(3)
            with col21:
                dt_admissao = st.text_input("Data Admissão (DDMMAAAA)", "", max_chars=10)
            with col22:
                carater_opt = st.selectbox("Caráter Atendimento", ["", "01 - Eletivo", "02 - Urgência"])
            with col22b:
                origem_opt = st.selectbox("Origem do Usuário", ["", "01 - Demanda Espontânea", "02 - Atenção Básica", "03 - Urgência", "04 - Outro CAPS"])
                
            col23, col24 = st.columns(2)
            with col23:
                cid_principal = st.text_input("CID Principal (Ex: F411)", "", max_chars=4)
            with col24:
                cid_associado = st.text_input("CID Associado (Opcional)", "", max_chars=4)
                
            st.markdown("##### Usuário de Álcool/Drogas")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                usu_droga = st.selectbox("Usuário de Drogas?", ["", "N", "S"])
            with col_d2:
                tipo_droga_opt = st.multiselect("Tipos", ["Álcool", "Crack", "Outras"])

            st.markdown("##### Cobertura ESF")
            col25, col26 = st.columns(2)
            with col25:
                cobertura_esf = st.selectbox("Cobertura ESF?", ["", "N", "S"])
            with col26:
                cnes_esf = st.text_input("CNES USF (Se ESF=S)", "", max_chars=7)
                
            col27, col28 = st.columns(2)
            with col27:
                destino_opt = st.selectbox("Destino Usuário", ["", "00 - Permanência", "01 - Continuidade Outro CAPS", "02 - Continuidade AB", "03 - Alta"])
            with col28:
                dt_conclusao = st.text_input("Data Alta/Conclusão (DDMMAAAA - Opcional)", "", max_chars=10)

        with tab_r:
            st.markdown("##### Selecione o Profissional")
            prof_selecionado = st.selectbox(
                "Profissional Executante", 
                list(CADASTRO_PROFISSIONAIS.keys()),
                key="select_profissional"
            )
            
            dados_prof = CADASTRO_PROFISSIONAIS.get(prof_selecionado, {"cns": "", "cbo": ""})
            
            col29, col30 = st.columns(2)
            with col29:
                dt_atend = st.text_input("Data do Procedimento (DDMMAAAA)", "", max_chars=10)
            with col30:
                procedimento = st.text_input("Procedimento SIGTAP (10 dígitos)", "", max_chars=10)
                
            col31, col32, col33 = st.columns(3)
            with col31:
                quantidade = st.text_input("Quantidade", "", max_chars=6)
            with col32:
                servico = st.text_input("Serviço (3 dígitos)", "", max_chars=3)
            with col33:
                classificacao = st.text_input("Classificação (3 dígitos)", "", max_chars=3)
                
            col34, col35, col36 = st.columns(3)
            with col34:
                cns_prof = st.text_input("CNS Profissional", value=dados_prof["cns"], max_chars=15, key="input_cns_prof")
            with col35:
                cbo = st.text_input("CBO Profissional", value=dados_prof["cbo"], max_chars=6, key="input_cbo_prof")
            with col36:
                local_realizacao = st.selectbox("Local Realização", ["", "C - CAPS", "T - Território"])

            submitted = st.form_submit_button("➕ Adicionar Lançamento ao Lote", type="primary")

        if submitted:
            cpf_limpo = ''.join(filter(str.isdigit, cpf_user)).zfill(11) if cpf_user.strip() else ""
            
            dt_nasc_conv = converter_data_para_sigtap(dt_nasc) if dt_nasc.strip() else None
            dt_admissao_conv = converter_data_para_sigtap(dt_admissao) if dt_admissao.strip() else None
            dt_atend_conv = converter_data_para_sigtap(dt_atend) if dt_atend.strip() else None
            dt_conclusao_conv = converter_data_para_sigtap(dt_conclusao) if dt_conclusao.strip() else "".ljust(8, ' ')

            if not nome_user.strip():
                st.error("O Nome do Paciente é obrigatório!")
            elif not nome_mae.strip():
                st.error("O Nome da Mãe é obrigatório!")
            elif not sexo:
                st.error("Selecione o sexo do paciente!")
            elif not dt_nasc_conv:
                st.error("Data de Nascimento inválida ou em branco! Use DDMMAAAA.")
            elif not dt_admissao_conv:
                st.error("Data de Admissão inválida ou em branco! Use DDMMAAAA.")
            elif not dt_atend_conv:
                st.error("Data do Procedimento inválida ou em branco! Use DDMMAAAA.")
            elif not raca_opt:
                st.error("Selecione a Raça/Cor!")
            elif not carater_opt:
                st.error("Selecione o Caráter do Atendimento!")
            elif not origem_opt:
                st.error("Selecione a Origem do Usuário!")
            elif not destino_opt:
                st.error("Selecione o Destino do Usuário!")
            elif not situacao_rua:
                st.error("Informe se está em Situação de Rua!")
            elif not usu_droga:
                st.error("Informe se é usuário de drogas!")
            elif not cobertura_esf:
                st.error("Informe a Cobertura ESF!")
            elif not codigo_tipo_log:
                st.error("Selecione o Tipo de Logradouro!")
            elif not local_realizacao:
                st.error("Selecione o Local de Realização!")
            elif len(cid_principal.strip()) < 4:
                st.error("O CID Principal deve ter 4 caracteres (Ex: F411)!")
            elif not procedimento.strip():
                st.error("O código do Procedimento SIGTAP é obrigatório!")
            else:
                str_droga = ""
                if usu_droga == "S":
                    if "Álcool" in tipo_droga_opt: str_droga += "A"
                    if "Crack" in tipo_droga_opt: str_droga += "C"
                    if "Outras" in tipo_droga_opt: str_droga += "O"
                str_droga = str_droga.ljust(3, ' ')[:3]
                
                cpf_final = cpf_limpo if len(cpf_limpo) == 11 else "00000000000"
                cns_final = cns_user.strip().zfill(15) if not cpf_limpo or len(cpf_limpo) != 11 else "000000000000000"

                novo_registro = {
                    "cnes": cnes.zfill(7), "prontuario": prontuario.strip().zfill(10), "cpf_user": cpf_final,
                    "cns_user": cns_final, "nome_user": nome_user.strip().upper(), "sexo": sexo[0],
                    "dt_nasc": dt_nasc_conv, "raca": raca_opt[:2], "etnia": etnia.strip().zfill(4) if etnia.strip() else "0000",
                    "nome_mae": nome_mae.strip().upper(), "nome_resp": (nome_resp.strip().upper() if nome_resp.strip() else nome_mae.strip().upper()),
                    "cep": cep.strip().zfill(8) if cep.strip() else "00000000", "municipio": municipio.strip().zfill(7) if municipio.strip() else "3122450", "bairro": bairro.strip().upper().ljust(30, ' ')[:30],
                    "tipo_log": codigo_tipo_log, "logradouro": logradouro.strip().upper().ljust(30, ' ')[:30],
                    "numero": numero.strip().zfill(5) if numero.strip() else "00000", "complemento": complemento.strip().upper().ljust(10, ' ')[:10],
                    "tel_cel": tel_cel.strip().zfill(11) if tel_cel.strip() else "00000000000", "tel_contato": tel_contato.strip().zfill(11) if tel_contato.strip() else "00000000000",
                    "situacao_rua": situacao_rua[0], "dt_admissao": dt_admissao_conv,
                    "carater_atend": carater_opt[:2], "origem_usuario": origem_opt[:2],
                    "cid_principal": cid_principal.strip().upper().ljust(4, ' ')[:4],
                    "cid_associado": cid_associado.strip().upper().ljust(4, ' ')[:4] if cid_associado.strip() else "".ljust(4, ' '),
                    "usu_droga": usu_droga[0], "tipo_droga": str_droga,
                    "cobertura_esf": cobertura_esf[0], "cnes_esf": cnes_esf.strip().zfill(7) if cobertura_esf.startswith("S") else "0".zfill(7),
                    "destino_usuario": destino_opt[:2], "dt_conclusao": dt_conclusao_conv,
                    "dt_atend": dt_atend_conv, "procedimento": procedimento.strip().zfill(10),
                    "quantidade": quantidade.strip().zfill(6) if quantidade.strip() else "000001", "servico": servico.strip().zfill(3) if servico.strip() else "115",
                    "classificacao": classificacao.strip().zfill(3) if classificacao.strip() else "001", "cns_prof": dados_prof["cns"].zfill(15),
                    "cbo": dados_prof["cbo"].zfill(6), "local_realizacao": local_realizacao[0]
                }
                st.session_state.atendimentos.append(novo_registro)
                st.success(f"Atendimento de {novo_registro['nome_user']} adicionado com sucesso!")

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
