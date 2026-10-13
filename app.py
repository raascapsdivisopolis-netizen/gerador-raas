import streamlit as st
import io
import json

st.set_page_config(page_title="Gerador RAAS-PS", layout="wide")

st.title("🗂️ Gerador de Remessa RAAS-PS (DATASUS)")

if "atendimentos" not in st.session_state:
    st.session_state.atendimentos = []

# --- PAINEL DE CONTROLE DA COMPETÊNCIA E BACKUP ---
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
    st.subheader("📝 Formulário de Digitação de Atendimento")
    
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
                dt_nasc = st.text_input("Data Nascimento (AAAAMMDD)", "19850907")
                
            col7, col8 = st.columns(2)
            with col7:
                raca_opt = st.selectbox("Raça/Cor", ["01 - Branca", "02 - Preta", "03 - Parda", "04 - Amarela", "05 - Indígena"], index=3)
            with col8:
                etnia = st.text_input("Etnia (4 dígitos - 0000 se não for indígena)", "0000", max_chars=4)
                
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
                tipo_log = st.text_input("Cód. Tipo Logradouro (3 dígitos - ex: 081 ou 000)", "081", max_chars=3)
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
                dt_admissao = st.text_input("Data Admissão (AAAAMMDD)", "20260812")
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
                dt_conclusao = st.text_input("Data Alta/Conclusão (Opcional)", "", max_chars=8)

        with tab_r:
            col29, col30 = st.columns(2)
            with col29:
                dt_atend = st.text_input("Data do Procedimento (AAAAMMDD)", "20260812")
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
                cns_prof = st.text_input("CNS Profissional (15 dígitos)", "702805644714369", max_chars=15)
            with col35:
                cbo = st.text_input("CBO Profissional (6 dígitos)", "322230", max_chars=6)
            with col36:
                local_realizacao = st.selectbox("Local Realização", ["C - CAPS", "T - Território"], index=0)

        submitted = st.form_submit_button("➕ Adicionar Lançamento ao Lote", type="primary")
        
        if submitted:
            cpf_limpo = ''.join(filter(str.isdigit, cpf_user)).zfill(11)
            if len(cpf_limpo) != 11 or cpf_limpo == "00000000000":
                st.error("Informe um CPF válido com 11 dígitos!")
            elif not nome_user or not nome_mae:
                st.error("Nome do Paciente e Nome da Mãe são obrigatórios!")
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
                    "cns_user": cns_user.zfill(15), "nome_user": nome_user, "sexo": sexo,
                    "dt_nasc": dt_nasc.zfill(8), "raca": raca_opt[:2], "etnia": etnia.zfill(4),
                    "nome_mae": nome_mae, "nome_resp": nome_resp if nome_resp else nome_mae,
                    "cep": cep.zfill(8), "municipio": municipio.zfill(7), "bairro": bairro.ljust(30, ' ')[:30],
                    "tipo_log": tipo_log.zfill(3), "logradouro": logradouro.ljust(30, ' ')[:30],
                    "numero": numero.zfill(5), "complemento": complemento.ljust(10, ' ')[:10],
                    "tel_cel": tel_cel.zfill(11), "tel_contato": tel_contato.zfill(11),
                    "situacao_rua": situacao_rua, "dt_admissao": dt_admissao.zfill(8),
                    "carater_atend": carater_opt[:2], "origem_usuario": origem_opt[:2],
                    "cid_principal": cid_principal.strip().ljust(4, ' ')[:4],
                    "cid_associado": cid_associado.strip().ljust(4, ' ')[:4] if cid_associado else "".ljust(4, ' '),
                    "usu_droga": usu_droga, "tipo_droga": str_droga,
                    "cobertura_esf": cobertura_esf, "cnes_esf": cnes_esf.zfill(7) if cobertura_esf == "S" else "0".zfill(7),
                    "destino_usuario": destino_opt[:2], "dt_conclusao": dt_conclusao.zfill(8) if dt_conclusao else "".ljust(8, ' '),
                    "dt_atend": dt_atend.zfill(8), "procedimento": procedimento.zfill(10),
                    "quantidade": quantidade.zfill(6), "servico": servico.zfill(3),
                    "classificacao": classificacao.zfill(3), "cns_prof": cns_prof.zfill(15),
                    "cbo": cbo.zfill(6), "local_realizacao": local_realizacao[0]
                }
                st.session_state.atendimentos.append(novo_registro)
                st.success(f"Atendimento de {nome_user} adicionado!")

with col_hist:
    st.subheader("📋 Histórico do Lote Atual")
    total_digitados = len(st.session_state.atendimentos)
    st.metric(label="Total de Registros Digitados", value=total_digitados)
    
    if total_digitados == 0:
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
                
                # LINHA 15 - Mapeada RIGOROSAMENTE conforme a tabela do PDF de ABRIL/2025
                linha15 = (
                    "15" +                                                 # 001-002 (2)  ras_codlinha_ad_corpo
                    codigo_uf +                                            # 003-004 (2)  ras_coduf
                    ano_mes +                                              # 005-010 (6)  ras_cmp
                    reg["cnes"] +                                          # 011-017 (7)  ras_codcnes
                    reg["cns_user"] +                                      # 018-032 (15) ras_cnspct
                    reg["dt_admissao"] +                                   # 033-040 (8)  ras_dtiinval
                    "".ljust(8, ' ') +                                     # 041-048 (8)  ras_dtfimval
                    reg["nome_user"].ljust(30, ' ')[:30] +                 # 049-078 (30) ras_nomepcnte
                    reg["prontuario"] +                                    # 079-088 (10) ras_npront
                    reg["nome_mae"].ljust(30, ' ')[:30] +                  # 089-118 (30) ras_nomemae
                    reg["logradouro"] +                                    # 119-148 (30) ras_logpcnte
                    reg["numero"] +                                        # 149-153 (5)  ras_numpcnte
                    reg["complemento"] +                                   # 154-163 (10) ras_cplpcnte
                    reg["cep"] +                                           # 164-171 (8)  ras_ceppcnte
                    reg["municipio"] +                                     # 172-178 (7)  ras_munpcnte
                    reg["dt_nasc"] +                                       # 179-186 (8)  ras_datanascim
                    reg["sexo"] +                                          # 187-187 (1)  ras_sexopcnte
                    reg["raca"] +                                          # 188-189 (2)  ras_raca
                    reg["nome_resp"].ljust(30, ' ')[:30] +                 # 190-219 (30) ras_nomeresp
                    "010" +                                                # 220-222 (3)  ras_nascpcnte (010=Brasil)
                    reg["etnia"] +                                         # 223-226 (4)  ras_etnia
                    reg["tel_contato"] +                                   # 227-237 (11) ras_telefone
                    reg["tel_cel"] +                                       # 238-248 (11) ras_celular
                    reg["destino_usuario"] +                               # 249-250 (2)  ras_motsaida
                    reg["dt_conclusao"] +                                  # 251-258 (8)  ras_dtobitoalta
                    reg["cid_principal"] +                                 # 259-262 (4)  pap_cidp
                    "".ljust(4, ' ') +                                     # 263-266 (4)  pap_cids1
                    "".ljust(4, ' ') +                                     # 267-270 (4)  pap_cids2
                    "".ljust(4, ' ') +                                     # 271-274 (4)  pap_cids3
                    reg["cid_associado"] +                                 # 275-278 (4)  ras_cidca
                    reg["carater_atend"] +                                 # 279-280 (2)  ras_CARATE
                    reg["origem_usuario"] +                                # 281-282 (2)  ras_origempcn
                    reg["cobertura_esf"] +                                 # 283-283 (1)  ras_cobertura_ESF
                    reg["cnes_esf"] +                                      # 284-290 (7)  ras_cnes_esd
                    "00001" +                                              # 291-295 (5)  ras_total_acoes
                    reg["destino_usuario"] +                               # 296-297 (2)  ras_dest_paciente
                    "RAS" +                                                # 298-300 (3)  ras_org
                    reg["situacao_rua"] +                                  # 301-301 (1)  ras_situacao_rua
                    reg["usu_droga"] +                                     # 302-302 (1)  ras_usu_droga
                    reg["tipo_droga"] +                                    # 303-305 (3)  ras_usu_tipo_droga
                    "".ljust(13, ' ') +                                    # 306-318 (13) ras_autorizacao
                    reg["bairro"] +                                        # 319-348 (30) ras_bairro
                    reg["tipo_log"] +                                      # 349-351 (3)  ras_cod_logradouro
                    "".ljust(40, ' ') +                                    # 352-391 (40) ras_email
                    reg["cpf_user"] +                                      # 392-402 (11) ras_cpfpct
                    "".ljust(4, ' ')                                       # 403-406 (4)  ras_filler
                )
                
                # LINHA 16 - Procedimentos da Atenção Psicossocial
                linha16 = (
                    "16" +                                                 # 001-002 (2)
                    codigo_uf +                                            # 003-004 (2)
                    ano_mes +                                              # 005-010 (6)
                    reg["cnes"] +                                          # 011-017 (7)
                    reg["cns_user"] +                                      # 018-032 (15)
                    reg["dt_admissao"] +                                   # 033-040 (8)
                    reg["procedimento"] +                                  # 041-050 (10)
                    reg["cbo"] +                                           # 051-056 (6)
                    reg["cns_prof"] +                                      # 057-071 (15)
                    reg["dt_atend"] +                                      # 072-079 (8)
                    reg["servico"] +                                       # 080-082 (3)
                    reg["classificacao"] +                                 # 083-085 (3)
                    reg["quantidade"] +                                    # 086-091 (6)
                    "RAS" +                                                # 092-094 (3)
                    reg["local_realizacao"] +                              # 095-095 (1)
                    reg["cpf_user"] +                                      # 096-106 (11)
                    "".ljust(4, ' ')                                       # 107-110 (4)
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
            
            st.success("Remessa gerada com sucesso!")
            st.download_button(
                label="📥 Baixar Arquivo Remessa AA312245",
                data=b_io,
                file_name="AA312245",
                mime="application/octet-stream"
            )
