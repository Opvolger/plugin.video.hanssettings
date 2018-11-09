import resources.lib.hanssettings

h = resources.lib.hanssettings.HansSettings(True)

print(h)

if (h):
    print(h.get_overzicht(h.get_dataoverzicht()))
    print('\n\n')
    print(h.get_name(h.get_datafromfilegithub('userbouquet.stream_nl_nationaal.tv'),'userbouquet.stream_nl_nationaal.tv'))
    print(h.get_items(h.get_datafromfilegithub('userbouquet.stream_nl_nationaal.tv')))
