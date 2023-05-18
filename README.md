# ALQAlign

under construction.

alqalign is a phoneme-based multilingual speech alignment toolkit. 

It is supposed to be able to handle ~8k language (at least theoretically). See the [full list](./doc/language.md) of supported languages. 

## Install

```bash
pip install git+https://github.com/xinjli/allosaurus.git@v2

python setup.py install
```

## Usage

The basic usage is as follows:

```bash
python -m alqalign.run  --lang=<your target language> --audio <path to your audio file> --text <path to your text file> --output=<path to an output directory>
```

where 

- `lang`: the target language id you want to use. it is default to `eng` (English). See the language section for details.
- `audio` is the path to your audio file or your audio directory. If it is a directory, all the audio files in the directory will be processed. the stem filename will be used as the utterance id to be aligned with the text file.
- `text` is the path to your text file or your text directory. If it is a directory, all the text files in the directory will be processed. the stem filename will be used as the utterance id to be aligned with the audio file.
- `output` is the path to your output directory. All results/artifacts will be stored here. See the output section for details

### Output

### Mode

There are three alignment `modes` in alqalign, it is default to `sentence`

- `sentence`: align at the sentence level. Each line in the text file is considered a separate sentence. timestamp of each sentence will be computed. In case there's only a single line, we will split the sentence by heuristics.  
- `word`: align at the word level. every word in the text file will be aggregated and get aligned. sentence boundary will not be considered.
- `phoneme`: align at the phoneme level. phonemes are derived from each word. 

### Slice

You can turn the `slice` flag to true, if you want to extract the aligned clip of each sentence/word/phoneme.

When it is true, the `output` directory will contain a `audios` directory, which will looks like the following where each file is an aligned audio clip.

```text
$ ls ./audios
000.wav  003.wav  006.wav  009.wav  012.wav  015.wav  018.wav  021.wav  024.wav  027.wav
001.wav  004.wav  007.wav  010.wav  013.wav  016.wav  019.wav  022.wav  025.wav
002.wav  005.wav  008.wav  011.wav  014.wav  017.wav  020.wav  023.wav  026.wav
```

### Language

You can specify the `lang`to your target language's ISO id. 3-char id or 2-char id is both fine, 2 char will be automatically remapped to 3-char interanlly. (e.g: `en` -> `eng`)

As mentioned previously, this toolkit is supposed to be able to handle ~8k language at least theoretically. Unfortunately, I cannot verify every language. If you find any language that is not working properly, please open an issue.

For some common languages, check the following table. For the full list of supported languages, see the [doc here](./doc/language.md).

| ISO id     |  language name     |
|--------------------|--------------------|
| abk      | Abkhazian |
| arb      | Standard Arabic |
| asm      | Assamese |
| ast      | Asturian |
| azb      | South Azerbaijani |
| bak      | Bashkir |
| bas      | Basa (Cameroon) |
| bel      | Belarusian |
| ben      | Bengali |
| bre      | Breton |
| bul      | Bulgarian |
| cat      | Catalan |
| ces      | Czech |
| chv      | Chuvash |
| ckb      | Central Kurdish |
| cmn      | Mandarin Chinese |
| cnh      | Haka Chin |
| cym      | Welsh |
| dan      | Danish |
| deu      | German |
| div      | Dhivehi |
| ekk      | Standard Estonian |
| ell      | Modern Greek (1453-) |
| eng      | English |
| epo      | Esperanto |
| eus      | Basque |
| fin      | Finnish |
| fra      | French |
| glg      | Galician |
| grn      | Paraguayan Guaraní |
| gug      | Paraguayan Guaraní |
| hau      | Hausa |
| hin      | Hindi |
| hsb      | Upper Sorbian |
| hun      | Hungarian |
| ibo      | Igbo |
| ina      | Interlingua (International Auxiliary Language Association) |
| ind      | Indonesian |
| ita      | Italian |
| jpn      | Japanese |
| kab      | Kabyle |
| kat      | Georgian |
| kaz      | Kazakh |
| kin      | Kinyarwanda |
| kir      | Kirghiz |
| kmr      | Northern Kurdish |
| lav      | Latvian |
| lit      | Lithuanian |
| lug      | Ganda |
| mal      | Malayalam |
| mar      | Marathi |
| mdf      | Moksha |
| mhr      | Eastern Mari |
| mkd      | Macedonian |
| mlt      | Maltese |
| mon      | Mongolian |
| mrj      | Western Mari |
| myv      | Erzya |
| nld      | Dutch |
| ory      | Oriya (individual language) |
| pes      | Iranian Persian |
| pol      | Polish |
| por      | Portuguese |
| ron      | Romanian |
| rus      | Russian |
| sah      | Yakut |
| skr      | Saraiki |
| slk      | Slovak |
| slv      | Slovenian |
| spa      | Spanish |
| sro      | Campidanese Sardinian |
| srp      | Serbian |
| swa      | Swahili (macrolanguage) |
| tam      | Tamil |
| tat      | Tatar |
| tha      | Thai |
| tig      | Tigre |
| tir      | Tigrinya |
| tur      | Turkish |
| twi      | Twi |
| uig      | Uighur |
| ukr      | Ukrainian |
| urd      | Urdu |
| uzb      | Uzbek |
| vie      | Vietnamese |
| vot      | Votic |


## Samples

There are a few samples in the `samples` directory.