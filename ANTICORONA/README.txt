🛡️ Sentinel Monitor v3.2
Sentinel Monitor é uma ferramenta de segurança proativa desenvolvida em Python. Ela combina o monitoramento de integridade de arquivos em tempo real com a análise de recursos do sistema (CPU/RAM) e vigilância de conexões de rede suspeitas.

🚀 Funcionalidades
Monitor de Arquivos (Watchdog): Detecta criações, modificações e deleções na pasta do projeto.

Análise de Rede: Lista conexões ESTABLISHED ativas, filtrando conexões locais e destacando IPs remotos.

Hardware Dashboard: Gráfico em tempo real da carga de CPU e uso de memória RAM via matplotlib.

Gerenciamento de Processos: Visualização dinâmica dos 15 processos mais ativos no sistema.

Sistema de Log: Registro automático de todos os eventos em um arquivo monitor_seguranca.txt.

Interface Moderna: GUI intuitiva com indicadores de status (LEDs) e modo escuro.

🛠️ Tecnologias Utilizadas
Python 3.12+

Tkinter (Interface Gráfica)

Psutil (Monitoramento de Sistema e Rede)

Watchdog (Eventos de Sistema de Arquivos)

Matplotlib (Gráficos em Tempo Real)

📦 Instalação e Requisitos
Clone o repositório:

Bash
git clone https://github.com/seu-usuario/sentinel-monitor.git
cd sentinel-monitor
Instale as dependências:

Bash
pip install watchdog matplotlib psutil
Execute o monitor:

Bash
python antiviruses.py
Nota: Para monitorar todas as conexões de rede e processos de sistema, recomenda-se executar o terminal como Administrador.

🖥️ Como Usar
Iniciar: Clique no botão verde "INICIAR" para começar a captura de dados.

Alertas: Caso um arquivo seja alterado ou uma conexão externa seja detectada, o log ficará em vermelho.

Pausar: Utilize o botão laranja para interromper o monitoramento sem fechar o app.

Logs: O arquivo monitor_seguranca.txt será criado na mesma pasta para consulta posterior.
