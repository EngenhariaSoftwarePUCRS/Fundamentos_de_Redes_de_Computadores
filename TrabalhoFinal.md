# Trabalho Final - Troca de Tabelas de Roteamento

## Integrantes

- [Carolina Ferreira](https://github.com/carolmic)
- [Felipe Freitas](https://github.com/felipefreitassilva)
- [Mateus Caçabuena](https://github.com/mateuscacabuena)
- [Nicholas Spolti](https://github.com/Nicholasspoltidesouza)

## Como rodar

### Requisitos

- Python ^3
- Readline (Windows)

### Passos

1. Clone o repositório
```bash
git clone https://github.com/EngenhariaSoftwarePUCRS/Fundamentos_de_Redes_de_Computadores.git
```

2. Instale as dependências (se estiver no windows)
Sugere-se utilizar o conda como gerenciador de pacotes
```bash
pip install -r requirements.txt
```

1. Execute o arquivo `router.py` passando opcionalmente o arquivo de roteadores, o IP local e o arquivo desejado de log (que deveriam ser automaticamente detectados)
Exemplo:
```bash
python router.py roteadores.txt 192.168.15.64 log.txt
```

### Possíveis problemas

- Verifique se a porta 9000 está liberada
- Verifique se o arquivo `roteadores.txt` está correto e está na mesma pasta que o arquivo `router.py`
- Verifique se o IP do roteador está correto
- Verifique se o IP dos outros roteadores estão corretos
- Verifique se é possível enviar um pacote para o IP dos outros roteadores (ping)
- Verifique o firewall (é possível que ele esteja bloqueando a comunicação)

## Features

- [x] Criar um arquivo de configuração `roteadores.txt` para IPs iniciais
- [x] Apresentar periodicamente a tabela de roteamento para o usuário
- [x] Enviar sua tabela a cada 15s
- [x] Criar tabela de roteamento (Lógica)
  - [x] Deve ter campos de origem, destino e métrica
  - [x] Deve receber uma nova entrada (tabela) e, para cada rota
    - [x] Se a rota for para o próprio roteador
      - [x] deve ser ignorada
    - [x] Se a rota não existir
      - [x] deve ser adicionada
      - [x] a métrica incrementada em 1
      - [x] o endereço de origem deve ser o endereço do roteador que enviou a linha
    - [x] Se existir e a métrica for menor
      - [x] a métrica deve ser atualizada
      - [x] o endereço de origem deve ser o endereço do roteador que enviou a linha
    - [x] Se uma rota deixar de existir
      - [x] deve ser removida
    - [x] Se a entrada gerar alteração na tabela deve anunciar imeadiatamente a mudança 
  - [x] Deve ter um método "print" que imprime a tabela para o usuário
  - [x] Deve ter um método "serialize" que converte a tabela em uma string para envio
- [x] Remover rotas inativos (a cada 35s)
- [x] Deve ser capaz de enviar mensagens de texto
- [x] Deve ser capaz de receber mensagens de texto
  - [x] Se a mensagem for para si, deve-se imprimir o texto
  - [x] Se a mensagem for para outro roteador, deve-se encaminhar a mensagem para o próximo roteador ou para o destino final
  - [x] Se a mensagem for para um roteador inexistente, deve-se informar o usuário
- [x] Utilizar socket UDP na porta 9000
