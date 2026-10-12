import streamlit as st
import io

st.set_page_config(page_title="Gerador RAAS-PS", layout="wide")

st.title("🗂️ Painel de Atendimentos - RAAS-PS (DATASUS)")

# Inicializa a lista de registros na sessão
if "atendimentos" not in st.session_state:
    st.session_state.atendimentos = []

# --- PAINEL DE CONTROLE DA COMPETÊNCIA (Área do Administrador / Geral) ---
st.container()
st.markdown("### ⚙️ Configuração da Competência")
col_comp1, col_comp2 = st.columns([1, 2])
with col_comp1:
    # Campo onde você define a competência (AAAAMM)
    competencia_input = st.text_input("Competência Ativa (AAAAMM)", "202608", help="Ex: 202608 para Agosto/2026")
with col_comp2:
    st.markdown(f"<br><h4 style='color: #2e6c80;'>Competência Aberta no Sistema: <b>{competencia_input}</b></h4>", unsafe_allow_html=True)

st.markdown("---")

col_form, col_hist = st.columns([1, 1.2])

with col_form:
    st.subheader("👤 1. Dados do Paciente")
    
    cnes = st.text_input("CNES da Unidade", "2119811")
    cbo = st.text_input("CBO do Profissional", "225142")
    cns_prof = st.text_input("CNS do Profissional", "702805644714369")
    
    st.markdown("---")
    nome_user = st.text_input("Nome do Paciente", "ISMAEL CESAR")
    cns_user = st.text_input("CNS do Paciente", "700000000000001")
    dt_nasc = st.text_input("Data de Nascimento (AAAAMMDD)", "19850907")
    sexo = st.selectbox("Sexo", ["M", "F"])
    raca = st.selectbox("Raça/Cor", ["01", "02", "03", "04", "05"], index=3)
    cep = st.text_input("CEP", "39912000")
    municipio = st.text_input("Município IBGE (c/ dígito)", "3122450")
    logradouro = st.text_input("Logradouro (Ex: RUA APOLINARIO BORGES)", "RUA APOLINARIO BORGES")
    
    st.subheader("🏥 2. Adicionar Atendimento / Procedimento")
    with st.form("form_procedimento", clear_on_submit=True):
        dt_atend = st.text_input("Data do Atendimento (AAAAMMDD)", "20260815")
        cid = st.text_input("CID Principal", "F411")
        procedimento = st.text_input("Procedimento (SIGTAP)", "0301080020")
        quantidade = st.text_input("Quantidade", "2")

        submitted_proc = st.form_submit_button("➕ Adicionar este Procedimento ao Paciente")
        
        if submitted_proc:
            novo_registro = {
                "cnes": cnes, "cbo": cbo, "cns_prof": cns_prof, "dt_atend": dt_atend,
                "nome_user": nome_user, "cns_user": cns_user, "dt_nasc": dt_nasc,
                "sexo": sexo, "raca": raca, "cep": cep, "municipio": municipio,
                "logradouro": logradouro, "cid": cid, "procedimento": procedimento, "quantidade": quantidade
            }
            st.session_state.atendimentos.append(novo_registro)
            st.success(f"Procedimento {procedimento} adicionado para {nome_user}!")

with col_hist:
    total_digitados = len(st.session_state.atendimentos)
    st.metric(label="📊 Total de Registros na Remessa", value=total_digitados)
    
    st.subheader("📋 Últimos Registros Adicionados")
    
    if total_digitados == 0:
        st.info("Nenhum atendimento adicionado ainda nesta sessão.")
    else:
        ultimos = list(enumerate(st.session_state.atendimentos))[-20:][::-1]
        
        for idx, reg in ultimos:
            with st.expander(f"👤 {reg['nome_user']} — Proc: {reg['procedimento']} (Data: {reg['dt_atend']})"):
                st.write(f"**CID:** {reg['cid']} | **Qtd:** {reg['quantidade']} | **CNS:** {reg['cns_user']}")
                st.write(f"**Endereço:** {reg['logradouro']}")
                
                if st.button("🗑️ Remover este registro", key=f"del_{idx}"):
                    st.session_state.atendimentos.pop(idx)
                    st.rerun()

    st.markdown("---")
    
    if total_digitados > 0:
        if st.button("💾 Gerar e Baixar Arquivo Oficial (AA312245)", type="primary"):
            ano_mes = ret_ano_mes = competencia_input.strip()
            codigo_uf = "31"
            data_geracao = "20261012"
            
            linhas_detalhe = []
            sub16_total = 0
            sub15_total = 0
            
            for reg in st.session_state.atendimentos:
                l15_log = reg["logradouro"].ljust(30, ' ')[:30]
                l15_nome = reg["nome_user"].ljust(30, ' ')[:30]
                
                sub16_total += int(reg["procedimento"]) + int(reg["quantidade"])
                sub15_total += int(reg["cnes"]) + int(reg["cns_user"])
                
                # Linha 15
                linha15 = (
                    "15" + codigo_uf + ano_mes + reg["cnes"].zfill(7) + reg["cns_user"].zfill(15) + reg["dt_atend"].zfill(8) + 
                    "".ljust(8, ' ') + l15_nome + "0001".zfill(10) + "".ljust(30, ' ') + 
                    l15_log + "00064".zfill(5) + "CASA      ".ljust(10, ' ') + reg["cep"].zfill(8) + 
                    reg["municipio"].zfill(7) + reg["dt_nasc"].zfill(8) + reg["sexo"].ljust(1, ' ') + 
                    reg["raca"].zfill(2) + l15_nome + "010    999999999993399999999921        " + 
                    reg["cid"].ljust(4, ' ') + "                0101S" + reg["cnes"].zfill(7) + "00001" + 
                    "00" + "RAS" + "N" + "N" + "   " + "".ljust(13, ' ') + "CENTRO                        ".ljust(30, ' ') + 
                    "081" + "".ljust(40, ' ') + "".zfill(11) + "    "
                )
                
                # Linha 16
                linha16 = (
                    "16" + codigo_uf + ano_mes + reg["cnes"].zfill(7) + reg["cns_user"].zfill(15) + reg["dt_atend"].zfill(8) + 
                    reg["procedimento"].zfill(10) + reg["cbo"].zfill(6) + reg["cns_prof"].zfill(15) + reg["dt_atend"].zfill(8) + 
                    "   " + "   " + reg["quantidade"].zfill(6) + "RAS" + "C" + "".zfill(11) + "    "
                )
                
                linhas_detalhe.append(linha15)
                linhas_detalhe.append(linha16)
            
            soma_ctrl = str(1111 + ((sub16_total + sub15_total) % 1111)).zfill(4)
            qtd_folhas_str = str(total_digitados).zfill(6)
            
            # Cabeçalho 01 com a competência dinâmica inserida no painel
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
            
            st.success("Arquivo gerado perfeitamente com todos os registros!")
            st.download_button(
                label="📥 Clique aqui para baixar o arquivo AA312245",
                data=b_io,
                file_name="AA312245",
                mime="application/octet-stream"
            )