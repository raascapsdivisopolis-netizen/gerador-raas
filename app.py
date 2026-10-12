import streamlit as st
import io
import json

st.set_page_config(page_title="Gerador RAAS-PS", layout="wide")

st.title("🗂️ Painel de Atendimentos - RAAS-PS (DATASUS)")

if "atendimentos" not in st.session_state:
    st.session_state.atendimentos = []

st.container()
st.markdown("### ⚙️ Configuração da Competência & Gerenciamento de Lote")
col_comp1, col_comp2, col_comp3 = st.columns([1, 1.5, 1.5])

with col_comp1:
    competencia_input = st.text_input("Competência Ativa (AAAAMM)", "202608", help="Ex: 202608 para Agosto/2026")

with col_comp2:
    if len(st.session_state.atendimentos) > 0:
        json_str = json.dumps(st.session_state.atendimentos, ensure_ascii=False, indent=4)
        st.download_button(
            label="💾 Salvar Rascunho Atual (Backup)",
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
        except Exception as e:
            st.error("Erro ao carregar o arquivo de backup.")

st.markdown("---")

col_form, col_hist = st.columns([1, 1.2])

with col_form:
    st.subheader("👤 1. Dados do Paciente (Identificação do Usuário)")
    
    cnes = st.text_input("CNES da Unidade Executante", "2119811")
    cbo = st.text_input("CBO do Profissional (Ex: 225125 / 251510 / 223505)", "225125")
    cns_prof = st.text_input("CNS do Profissional", "702805644714369")
    
    st.markdown("---")
    cpf_user = st.text_input("CPF do Paciente (Apenas números - 11 dígitos)", "", max_chars=11)
    nome_user = st.text_input("Nome do Paciente", "")
    nome_mae = st.text_input("Nome da Mãe do Paciente", "")
    dt_nasc = st.text_input("Data de Nascimento (AAAAMMDD)", "")
    sexo = st.selectbox("Sexo", ["M", "F"])
    raca = st.selectbox("Raça/Cor", ["01", "02", "03", "04", "05"], index=3)
    cep = st.text_input("CEP", "39912000")
    municipio = st.text_input("Município IBGE (c/ dígito)", "3122450")
    logradouro = st.text_input("Logradouro (Ex: RUA JOSE FERRAZ)", "")
    
    st.markdown("---")
    st.subheader("📋 Dados da Cobertura e Atendimento")
    
    situacao_rua = st.selectbox("Em Situação de Rua?", ["N", "S"], index=0)
    
    col_esf1, col_esf2 = st.columns(2)
    with col_esf1:
        cobertura_esf = st.selectbox("Cobertura ESF/PSF?", ["S", "N"], index=0)
    with col_esf2:
        cnes_esf = st.text_input("CNES da USF/PSF (Se Cobertura ESF = S)", "2119811")
        
    origem_usuario = st.selectbox("Origem do Usuário", ["01 - DEMANDA ESPONTANEA", "02 - ENCAMINHAMENTO RESIDENCIAL", "03 - ENCAMINHAMENTO UBS", "04 - OUTROS"], index=0)
    destino_usuario = st.selectbox("Destino do Usuário", ["01 - PERMANENCIA/CONTINUIDADE", "02 - ALTA", "03 - ENCAMINHAMENTO"], index=0)
    
    col_serv, col_class = st.columns(2)
    with col_serv:
        servico = st.text_input("Serviço (3 dígitos)", "115")
    with col_class:
        classificacao = st.text_input("Classificação (2 dígitos)", "001")
    
    st.subheader("🏥 2. Adicionar Atendimento / Procedimento")
    with st.form("form_procedimento", clear_on_submit=True):
        dt_atend = st.text_input("Data do Atendimento / Admissão (AAAAMMDD)", "")
        cid = st.text_input("CID Principal (4 dígitos - Ex: F411)", "F411", max_chars=4)
        procedimento = st.text_input("Procedimento (SIGTAP - 10 dígitos)", "0301080020")
        quantidade = st.text_input("Quantidade", "1")

        submitted_proc = st.form_submit_button("➕ Adicionar este Procedimento ao Paciente")
        
        if submitted_proc:
            cpf_limpo = ''.join(filter(str.isdigit, cpf_user)).zfill(11)
            if len(cpf_limpo) != 11:
                st.error("Por favor, informe um CPF válido com exatamente 11 dígitos!")
            elif not nome_user or not nome_mae:
                st.error("Nome do Paciente e Nome da Mãe são obrigatórios!")
            elif len(cid.strip()) < 3:
                st.error("Informe um CID válido com pelo menos 3 ou 4 caracteres (Ex: F411)!")
            else:
                novo_registro = {
                    "cnes": cnes, "cbo": cbo, "cns_prof": cns_prof, "dt_atend": dt_atend,
                    "nome_user": nome_user, "nome_mae": nome_mae, "cpf_user": cpf_limpo,
                    "cns_user": "0".zfill(15), "dt_nasc": dt_nasc, "sexo": sexo, "raca": raca,
                    "cep": cep, "municipio": municipio, "logradouro": logradouro,
                    "situacao_rua": situacao_rua, "cobertura_esf": cobertura_esf,
                    "cnes_esf": cnes_esf if cobertura_esf == "S" else "0".zfill(7),
                    "origem_usuario": origem_usuario[:2], "destino_usuario": destino_usuario[:2],
                    "cid": cid.strip().ljust(4, ' '),
                    "servico": servico, "classificacao": classificacao,
                    "procedimento": procedimento, "quantidade": quantidade
                }
                st.session_state.atendimentos.append(novo_registro)
                st.success(f"Procedimento {procedimento} adicionado para {nome_user} (CPF: {cpf_limpo})!")

with col_hist:
    total_digitados = len(st.session_state.atendimentos)
    st.metric(label="📊 Total de Registros na Remessa", value=total_digitados)
    
    st.subheader("📋 Últimos Registros Adicionados")
    
    if total_digitados == 0:
        st.info("Nenhum atendimento adicionado ainda nesta sessão.")
    else:
        ultimos = list(enumerate(st.session_state.atendimentos))[-20:][::-1]
        
        for idx, reg in ultimos:
            with st.expander(f"👤 {reg['nome_user']} — CPF: {reg['cpf_user']} — Proc: {reg['procedimento']}"):
                st.write(f"**Mãe:** {reg['nome_mae']} | **Data:** {reg['dt_atend']} | **CID:** {reg['cid']}")
                st.write(f"**ESF:** {reg['cobertura_esf']} (CNES: {reg['cnes_esf']}) | **Qtd:** {reg['quantidade']}")
                
                if st.button("🗑️ Remover este registro", key=f"del_{idx}"):
                    st.session_state.atendimentos.pop(idx)
                    st.rerun()

    st.markdown("---")
    
    if total_digitados > 0:
        if st.button("💾 Gerar e Baixar Arquivo Oficial (AA312245)", type="primary"):
            ano_mes = competencia_input.strip()
            codigo_uf = "31"
            data_geracao = "20261012"
            
            linhas_detalhe = []
            sub16_total = 0
            sub15_total = 0
            
            for reg in st.session_state.atendimentos:
                l15_nome = reg["nome_user"].ljust(30, ' ')[:30]
                l15_mae = reg["nome_mae"].ljust(30, ' ')[:30]
                l15_log = reg["logradouro"].ljust(30, ' ')[:30]
                l15_serv = reg["servico"].zfill(3)[:3]
                l15_class = reg["classificacao"].zfill(2)[:2]
                l15_cid = reg["cid"].ljust(4, ' ')[:4]
                l15_cnes_esf = reg["cnes_esf"].zfill(7)[:7]
                
                sub16_total += int(reg["procedimento"]) + int(reg["quantidade"])
                sub15_total += int(reg["cnes"]) + int(reg["cns_user"])
                
                # Linha 15 perfeitamente estruturada conforme os campos da tela do RAAS
                linha15 = (
                    "15" + codigo_uf + ano_mes + reg["cnes"].zfill(7) + reg["cns_user"].zfill(15) + reg["dt_atend"].zfill(8) + 
                    "".ljust(8, ' ') + l15_nome + "0001".zfill(10) + "".ljust(30, ' ') + 
                    l15_log + "00064".zfill(5) + "CASA      ".ljust(10, ' ') + reg["cep"].zfill(8) + 
                    reg["municipio"].zfill(7) + reg["dt_nasc"].zfill(8) + reg["sexo"].ljust(1, ' ') + 
                    reg["raca"].zfill(2) + l15_mae + l15_serv + l15_class + "    999999999993399999999921        " + 
                    l15_cid + "                " + reg["origem_usuario"] + reg["destino_usuario"] + reg["cobertura_esf"] + 
                    l15_cnes_esf + "00001" + reg["situacao_rua"] + "RAS" + "N" + "N" + "   " + "".ljust(13, ' ') + 
                    "CENTRO                        ".ljust(30, ' ') + "081" + "".ljust(40, ' ') + reg["cpf_user"].zfill(11) + "    "
                )
                
                # Linha 16
                linha16 = (
                    "16" + codigo_uf + ano_mes + reg["cnes"].zfill(7) + reg["cns_user"].zfill(15) + reg["dt_atend"].zfill(8) + 
                    reg["procedimento"].zfill(10) + reg["cbo"].zfill(6) + reg["cns_prof"].zfill(15) + reg["dt_atend"].zfill(8) + 
                    "   " + "   " + reg["quantidade"].zfill(6) + "RAS" + "C" + reg["cpf_user"].zfill(11) + "    "
                )
                
                linhas_detalhe.append(linha15)
                linhas_detalhe.append(linha16)
            
            soma_ctrl = str(1111 + ((sub16_total + sub15_total) % 1111)).zfill(4)
            qtd_folhas_str = str(total_digitados).zfill(6)
            
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
