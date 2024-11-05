from router import Router

if __name__ == '__main__':
    router_ip = ''
    router = Router(router_ip, 'roteadores.txt')
    router.check_presence()
    router.start()
