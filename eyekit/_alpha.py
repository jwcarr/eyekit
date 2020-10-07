special_characters_by_language = {
	'Bulgarian': 'АБВГДЕЖЗИЙЍКЛМНОПРСТУФХЦЧШЩЪЬЮЯабвгдежзийѝклмнопрстуфхцчшщъьюя',
	'Croatian': 'ČĆĐŠŽčćđšž',
	'Czech': 'ÁČĎÉĚÍŇÓŘŠŤÚŮÝŽáčďéěíňóřšťúůýž',
	'Danish': 'ÆØÅæøå',
	'Estonian': 'ŠŽÕÄÖÜšžõäöü',
	'Finnish': 'ÅÄÖåäö',
	'French': 'ÇÉÀÈÙÂÊÎÔÛËÏÜŸŒçéàèùâêîôûëïüÿœ',
	'German': 'ÄÖÜäöüß',
	'Greek': 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫαβγδεζηθικλμνξοπρσςτυφχψωάέήίόύώϊϋΐΰ',
	'Hungarian': 'ÁÉÍÓÖŐÚÜŰáéíóöőúüű',
	'Irish': 'ÁÉÍÓÚáéíóú',
	'Italian': 'ÀÉÈÍÌÓÒÚÙàéèíìóòúù',
	'Latvian': 'ĀČĒĢĪĶĻŅŠŪŽāčēģīķļņšūž',
	'Lithuanian': 'ĄČĘĖĮŠŲŪŽąčęėįšųūž',
	'Maltese': 'ĊĠĦŻċġħż',
	'Norwegian': 'ÆØÅæøå',
	'Polish': 'ĄĆĘŁŃÓŚŹŻąćęłńóśźż',
	'Portuguese': 'ÁÂÃÀÇÉÊÍÓÔÕÚáâãàçéêíóôõú',
	'Romanian': 'ĂÂÎȘȚăâîșț',
	'Russian': 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя',
	'Slovak': 'ÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽáäčďéíĺľňóôŕšťúýž',
	'Slovene': 'ČŠŽčšž',
	'Spanish': 'ÑÁÉÍÓÚÜñáéíóúü',
	'Swedish': 'ÅÄÖåäö',
	'Turkish': 'ÇĞİÖŞÜçşğıiöü'
}

special_characters = []
for characters in special_characters_by_language.values():
	special_characters.extend(characters)

characters = 'A-Za-z' + ''.join(set(special_characters))
