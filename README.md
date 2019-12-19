# anonybot
Um protótipo de bot de Telegram para envio de mensagens anônimas

## Instalação
Para instalar as dependências é necessário ter o pacote `pip` instalado e, opcionalmente, um `virtualenv` ativo. A instalação é feita com `pip install -r requirements.txt`.

## Configuração
Para que o bot funcione, são necessárias algumas configurações simples.
Crie um arquivo `.env` no diretório do código, e preencha as seguintes variáveis:
- `DB_ADDR = <url do banco de dados a ser utilizado>`
- `BOT_TOKEN = <token de bot do Telegram, adquirido ao inscrever um novo bot em @botfather>`

Após preenchidas as variáveis necessárias para a configuração, basta executar o bot com `python anonybot.py`.

## Código
Criado com ajuda da biblioteca [aiogram](https://github.com/aiogram/aiogram), cada função no arquivo `.py` é um comando diferente que o bot pode executar, cujo identificador é encontrado em `commands=[<comando>]` antes da definição da função.
São 6 comandos:
- `/send <id>`: Ao responder para uma mensagem com esse comando e um Telegram user id, a mensagem é guardada no banco de dados do servidor, e o receptor recebe um alerta de que tem uma nova mensagem.
- `/receive`: Ao executar, todas as mensagens destinadas ao usuário no banco são mostradas, e então apagadas do banco.
- `/drop`: Ao executar, apaga todas as mensagens destinadas ao usuário no banco, sem mostrar seu conteúdo.
- `/status`: Ao executar, mostra quantas mensagens destinadas ao usuário existem no banco.
- `/help`: Mostra os comandos que podem ser utilizados.
- `/start`: Utilizado quando o bot é iniciado, mostra uma mensagem inicial de ajuda, e quantas mensagens já existem para o usuário (se houver alguma).
