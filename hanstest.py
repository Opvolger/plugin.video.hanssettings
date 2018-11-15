import resources.lib.hanssettings

h = resources.lib.hanssettings.HansSettings()

print(h)

if (h):
    #print(h.get_overzicht(h.get_dataoverzicht()))
    print('\n\n')
    linkdata = h.get_datafromfilegithub('userbouquet.stream_muziek.tv')
    #linkdata = h.get_datafromfilegithub('userbouquet.stream_nl_nationaal.tv')
    #print(h.get_name(linkdata,'userbouquet.stream_nl_nationaal.tv'))
    #print(h.get_items(linkdata))
    print(h.get_items_subfolder(linkdata, '1'))
