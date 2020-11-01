import bluetooth, os 


def buscaBluetooth():

    print("Buscando...")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True,flush_cache=True, lookup_class=False)

    print("Achado {} dispositivos".format(len(nearby_devices)))

    for addr, name in nearby_devices:
        try:
            print("   {} - {}".format(addr, name))
        except UnicodeEncodeError:
            print("   {} - {}".format(addr, name.encode("utf-8", "replace")))
    
    return len(nearby_devices)

def apagaCache():

    os.system("./deletaCache.sh")

