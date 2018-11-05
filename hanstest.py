import resources.lib.hanssettings

h = resources.lib.hanssettings.HansSettings()

print(h)

if (h):
    print(h.get_overzicht())
    print('\n\n')
    print(h.get_items('userbouquet.stream_nl_nationaal.tv'))
