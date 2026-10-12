import streamlit as st
import io
import json

st.set_page_config(page_title="Gerador RAAS-PS", layout="wide")

st.title("🗂️ Painel Completo de Atendimentos - RAAS-PS (DATASUS)")

if "atendimentos" not in st.session_state:
    st.session_state.atendimentos = []

st.container()
st.markdown("### ⚙️ Configuração da Competência & Gerenciamento de Lote")
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
            st.error("Erro ao carregar o arquivo de backup.")

st.markdown("---")

# Formulário dividido exatamente nas abas do RAAS
with st.form("form_raas_completo", clear_on_submit=False):
    
    tab_p, tab_a, tab_r = st.tabs(["[ P ] Identificação do Usuário", "[ A ] Identificação do Atendimento", "[ R ] Ações Realizadas"])
    
    with tab_p:
        st.subheader("Dados Cadastrais do Paciente")
        cnes = st.text_input("CNES da Unidade Executante", "2119811")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            prontuario = st.text_input("Prontuário", "0000000001", max_chars=10)
        with col2:
            cpf_user = st.text_input("CPF do Paciente (11 dígitos)", "", max_chars=11)
        with col3:
            cns_user = st.text_input("CNS do Paciente (15 dígitos ou Zeros)", "000000000000000", max_chars=15)
            
        col4, col5, col6 = st.columns(3)
        with col4:
            nome_user = st.text_input("Nome do Paciente", "")
        with col5:
            sexo = st.selectbox("Sexo", ["M", "F"])
        with col6:
            dt_nasc = st.text_input("Data de Nascimento (AAAAMMDD)", "")
            
        col7, col8 = st.columns(2)
        with col7:
            raca = st.selectbox("Raça/Cor", ["01 - BRANCA", "02 - PRETA", "03 - PARDA", "04 - AMARELA", "05 - INDIGENA"], index=3)
        with col8:
            etnia = st.text_input("Etnia (2 dígitos)", "00", max_chars=2)
            
        col9, col10 = st.columns(2)
        with col9:
            nome_mae = st.text_input("Nome da Mãe", "")
        with col10:
            nome_resp = st.text_input("Nome do Responsável", "")
            
        st.markdown("##### Endereço")
        col11, col12, col13 = st.columns(3)
        with col11:
            cep = st.text_input("CEP", "39912000", max_chars=8)
        with col12:
            municipio = st.text_input("Município IBGE (c/ dígito)", "3122450", max_chars=7)
        with col13:
            bairro = st.text_input("Bairro", "CENTRO")
            
        col14, col15, col16 = st.columns(3)
        with col14:
            # Tipo de logradouro numérico conforme o erro 0026 (ex: 000 ou 070)
            tipo_log = st.text_input("Tipo de Logradouro (Código - ex: 000 ou 070)", "000", max_chars=3)
        with col15:
            logradouro = st.text_input("Nome do Logradouro", "RUA JOSE FERRAZ")
        with col16:
            numero = st.text_input("Número", "00064", max_chars=5)
            
        col17, col18, col19, col20 = st.columns(4)
        with col17:
            complemento = st.text_input("Complemento", "CASA")
        with col18:
            tel_cel = st.text_input("Tel. Celular", "993399999")
        with col19:
            tel_contato = st.text_input("Tel. Contato", "99999999")
        with col20:
            situacao_rua = st.selectbox("Em Situação de Rua?", ["N", "S"], index=0)

    with tab_a:
        st.subheader("Dados do Atendimento e Vínculos")
        
        col21, col22 = st.columns(2)
        with col21:
            dt_admissao = st.text_input("Data de Admissão (AAAAMMDD)", "")
        with col22:
            origem_usuario = st.selectbox("Origem do Usuário", ["01 - DEMANDA ESPONTANEA", "02", "03", "04"], index=0)
            
        col23, col24 = st.columns(2)
        with col23:
            cid_principal = st.text_input("CID Principal (4 dígitos - Ex: F411)", "F411", max_chars=4)
        with col24:
            cid_associado = st.text_input("CID Causas Associadas (Opcional)", "", max_chars=4)
            
        st.markdown("##### Cobertura de Estratégia Saúde da Família (ESF)")
        col25, col26 = st.columns(2)
        with col25:
            cobertura_esf = st.selectbox("Cobertura ESF? (S ou N)", ["N", "S"], index=0)
        with col26:
            cnes_esf = st.text_input("CNES da USF (Obrigatório se ESF = S)", "0000000", max_chars=7)
            
        col27, col28 = st.columns(2)
        with col27:
            destino_usuario = st.selectbox("Destino do Usuário", ["01 - CONTINUIDADE", "02 - ALTA", "03"], index=0)
        with col28:
            dt_conclusao = st.text_input("Data de Conclusão / Alta (AAAAMMDD - Opcional)", "", max_chars=8)

    with tab_r:
        st.subheader("Dados das Ações Realizadas (Procedimentos)")
        
        col29, col30 = st.columns(2)
        with col29:
            dt_atend = st.text_input("Data de Realização da Ação (AAAAMMDD)", "")
        with col30:
            procedimento = st.text_input("Procedimento (SIGTAP - 10 dígitos)", "0301080020", max_chars=10)
            
        col31, col32, col33 = st.columns(3)
        with col31:
            quantidade = st.text_input("Quantidade", "1", max_chars=6)
        with col32:
            servico = st.text_input("Serviço (3 dígitos)", "115", max_chars=3)
        with col33:
            classificacao = st.text_input("Classificação (2 dígitos)", "001", max_chars=2)
            
        col34, col35 = st.columns(2)
        with col34:
            cns_prof = st.text_input("CNS do Profissional (15 dígitos)", "702805644714369", max_chars=15)
        with col35:
            cbo = st.text_input("CBO do Profissional (6 dígitos)", "225125", max_chars=6)

    st.markdown("---")
    submitted_proc = st.form_submit_button("➕ Adicionar Atendimento / Procedimento à Remessa", type="primary")
    
    if submitted_proc:
        cpf_limpo = ''.join(filter(str.isdigit, cpf_user)).zfill(11)
        if len(cpf_limpo) != 11:
            st.error("Informe um CPF válido com exatamente 11 dígitos na aba [ P ]!")
        elif not nome_user or not nome_mae:
            st.error("Nome do Paciente e Nome da Mãe são obrigatórios na aba [ P ]!")
        elif len(cid_principal.strip()) < 4:
            st.error("Informe um CID Principal completo com 4 caracteres (Ex: F411) na aba [ A ]!")
        else:
            novo_registro = {
                "cnes": cnes, "prontuario": prontuario.zfill(10), "cpf_user": cpf_limpo,
                "cns_user": cns_user.zfill(15), "nome_user": nome_user, "sexo": sexo,
                "dt_nasc": dt_nasc, "raca": raca[:2], "etnia": etnia.zfill(2),
                "nome_mae": nome_mae, "nome_resp": nome_resp, "cep": cep.zfill(8),
                "municipio": municipio.zfill(7), "bairro": bairro.ljust(30, ' ')[:30],
                "tipo_log": tipo_log.zfill(3), "logradouro": logradouro.ljust(30, ' ')[:30],
                "numero": numero.zfill(5), "complemento": complemento.ljust(10, ' ')[:10],
                "situacao_rua": situacao_rua, "dt_admissao": dt_admissao,
                "origem_usuario": origem_usuario[:2], "cid_principal": cid_principal.strip().ljust(4, ' ')[:4],
                "cid_associado": cid_associado.strip().ljust(4, ' ')[:4] if cid_associado else "".ljust(4, ' '),
                "cobertura_esf": cobertura_esf, "cnes_esf": cnes_esf.zfill(7) if cobertura_esf == "S" else "0".zfill(7),
                "destino_usuario": destino_usuario[:2], "dt_conclusao": dt_conclusao.zfill(8) if dt_conclusao else "".ljust(8, ' '),
                "dt_atend": dt_atend, "procedimento": procedimento.zfill(10), "quantidade": quantidade.zfill(6),
                "servico": servico.zfill(3), "classificacao": classificacao.zfill(2),
                "cns_prof": cns_prof.zfill(15), "cbo": cbo.zfill(6)
            }
            st.session_state.atendimentos.append(novo_registro)
            st.success(f"Atendimento de {nome_user} adicionado com sucesso!")

st.markdown("---")
st.subheader("📋 Painel de Controle da Remessa")

total_digitados = len(st.session_state.atendimentos)
st.metric(label="Total de Atendimentos na Remessa", value=total_digitados)

if total_digitados > 0:
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
            
            # Linha 15 (Mapeada com rigor para cada posição do DATASUS)
            linha15 = (
                "15" + codigo_uf + ano_mes + reg["cnes"].zfill(7) + reg["cns_user"] + reg["dt_admissao"] + 
                "".ljust(8, ' ') + reg["nome_user"].ljust(30, ' ')[:30] + reg["prontuario"] + "".ljust(30, ' ') + 
                reg["logradouro"] + reg["numero"] + reg["complemento"] + reg["cep"] + 
                reg["municipio"] + reg["dt_nasc"] + reg["sexo"] + reg["raca"] + reg["nome_mae"].ljust(30, ' ')[:30] + 
                reg["servico"] + reg["classificacao"] + "    999999999993399999999921        " + 
                reg["cid_principal"] + reg["cid_associado"] + reg["origem_usuario"] + reg["destino_usuario"] + 
                reg["cobertura_esf"] + reg["cnes_esf"] + "0001" + reg["situacao_rua"] + "RAS" + "N" + "N" + "   " + 
                "".ljust(13, ' ') + reg["bairro"] + "081" + "".ljust(40, ' ') + reg["cpf_user"] + "    "
            )
            
            # Linha 16
            linha16 = (
                "16" + codigo_uf + ano_mes + reg["cnes"].zfill(7) + reg["cns_user"] + reg["dt_atend"] + 
                reg["procedimento"] + reg["cbo"] + reg["cns_prof"] + reg["dt_atend"] + 
                "   " + "   " + reg["quantidade"] + "RAS" + "C" + reg["cpf_user"] + "    "
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
        
        st.success("Arquivo gerado com sucesso!")
        st.download_button(
            label="📥 Baixar Arquivo AA312245",
            data=b_io,
            file_name="AA312245",
            mime="application/octet-stream"
        )
