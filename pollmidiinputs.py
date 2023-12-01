import mido

def list_midi_ports():
    print("Available MIDI input ports:")
    for port_name in mido.get_input_names():
        print(port_name)

if __name__ == "__main__":
    list_midi_ports()
