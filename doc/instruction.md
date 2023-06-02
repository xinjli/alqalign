# Instruction

## Usage

The basic usage with main configures is as follows:

```bash
python -m alqalign.run  --lang=<your target language> --audio <path to your audio file> --text <path to your text file> --output=<path to an output directory>
```

where 

- `lang`: the target language id you want to use. it is default to `eng` (English). See the language section for details.
- `audio` is the path to your audio file or your audio directory. If it is a directory, all the audio files in the directory will be processed. the stem filename will be used as the utterance id to be aligned with the text file.
- `text` is the path to your text file or your text directory. If it is a directory, all the text files in the directory will be processed. the stem filename will be used as the utterance id to be aligned with the audio file.
- `output` is the path to your output directory. All results/artifacts will be stored here. See the output section for details

### audio input

`audio` can point to a single audio file or a directory. 

If it is pointing to a single file

- it can be any audio format as long as torchaudio can read it

If it is pointing to a directory

- all the audio files in the directory will be processed. 
- the stem filename will be used as the original utterance id to be aligned with the text file. 


### text input

`text` is similar to `audio`, it can point to a single text file or a directory.

### output

`output` should be a directory. All results/artifacts will be stored here.

`output_format` config controls the output format It can be either `ctm` or `kaldi` for now.

#### ctm

In the case of `ctm`, there will be a `result.ctm` file in the output directory. It will look like the following:

```text
audio 1 0.26 1.59 吾輩は猫である -0.34
audio 1 1.85 1.59 名前はまだ無い -0.22
```

where 

- the 1st field is the original utterance id (i.e stem filename)
- the 2nd field is always 1 (channel id)
- the 3rd field is the start time in seconds
- the 4th field is the duration in seconds
- the 5th field is the aligned text
- the 6th field is the confidence score

#### kaldi

In the case of `kaldi`, it will serialize those info into three files: `segments`, `text`, `score`

`segments` is a kaldi-style segments file, which looks like the following:

```text
utt1-00000-0000028-0000367 utt1 0.28 3.67
utt1-00001-0000384-0000917 utt1 3.85 9.17
```

where the 1st field is the segment utterance id, the 2nd field is the original utterance id (i.e stem filename), the 3rd field is the start time in seconds, the 4th field is the end time in seconds.

`text` is a kaldi-style text file, which looks like the following:

```text
utt1-00000-0000028-0000367 A PROGRAMMER WALKS TO THE BUTCHER SHOP AND BUYS A KILO OF MEAT.
utt1-00001-0000384-0000917 AN HOUR LATER HE COMES BACK UPSET THAT THE BUTCHER SHORTCHANGED HIM BY 24 GRAMS.
```

`score` is not a kaldi standard file, it is a file to keep track of confidence score assigned to each segment. A higher score (close to 0) indicates a good alignment.

It looks like the following:

```text
utt1-00000-0000028-0000367 -0.14
utt1-00001-0000384-0000917 -0.13
```


### mode

There are three alignment `modes` in alqalign, it is default to `sentence`

- `sentence`: align at the sentence level. Each line in the text file is considered a separate sentence. timestamp of each sentence will be computed. In case there's only a single line, we will split the sentence by heuristics.  
- `word`: align at the word level. every word in the text file will be aggregated and get aligned. sentence boundary will not be considered.
- `phoneme`: align at the phoneme level. phonemes are derived from each word. 

### slice

You can turn the `slice` flag to true, if you want to extract the aligned clip of each sentence/word/phoneme.

When it is true, the `output` directory will contain a `audios` directory, which will looks like the following where each file is an aligned audio clip.

The filename is its segmnet utterance id. The output format is always `wav` sampled at 16k with 1 channel for now.

```text
$ ls ./audios
utt1-00000-0000028-0000367.wav
utt1-00001-0000384-0000917.wav
```

### language

You can specify the `lang`to your target language's ISO id. 3-char id or 2-char id is both fine, 2 char will be automatically remapped to 3-char interanlly. (e.g: `en` -> `eng`)

As mentioned previously, this toolkit is supposed to be able to handle ~8k language at least theoretically. Unfortunately, I cannot verify every language. If you find any language that is not working properly, please open an issue.

For some common languages, check the following table. For the full list of supported languages, see the [doc here](./language.md).

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

### English

There is one English sample in the `samples/eng` directory. It contains two files:

- `utt.wav`: a wav file containing 10 seconds of speech.
- `utt.txt`: a text file containing two lines as follows:

```text
A programmer walks to the butcher shop and buys a kilo of meat.
An hour later he comes back upset that the butcher shortchanged him by 24 grams.
```

To apply the alignment, you can run the following command:

```
python -m alqalign.run --lang=eng --audio=./samples/eng/utt.wav --text=./samples/eng/utt.txt --output=./samples/output/eng
```

The output will be in the `./samples/output/eng` directory. It contains a few files including

- `segments`: containing timestamps
- `text`: containing the aligned text

In this sample, the `segments` is

```text
utt-00000-0000028-0000367 utt 0.28 3.67
utt-00001-0000384-0000917 utt 3.85 9.17
```

and `text` is

```text
utt-00000-0000028-0000367 A PROGRAMMER WALKS TO THE BUTCHER SHOP AND BUYS A KILO OF MEAT.
utt-00001-0000384-0000917 AN HOUR LATER HE COMES BACK UPSET THAT THE BUTCHER SHORTCHANGED HIM BY 24 GRAMS.
```

If you run the command with `--slice=true`, it will also produce those audios in the `./samples/output/eng/audios` directory.

```text
utt-00000-0000028-0000367.wav  
utt-00001-0000384-0000917.wav
```

### English Batch

The sample in `samples/batch` is an example using batch mode. It will run alignment for 2 files.

It contains two directories:

- `samples/batch/text`: contains two text files `utt1.txt` and `utt2.txt`
- `samples/batch/audio`: contains two wav files `utt1.wav` and `utt2.wav`

By running the following command, it will align the two files and produce the output in the `./samples/output/batch` directory.

```
python -m alqalign.run --lang=eng --audio=./samples/batch/audio --text=./samples/batch/text --output=./samples/output/batch
```

### Mandarin

There is one Mandarin sample in the `samples/cmn` directory. You can run the following command to align it.

```
python -m alqalign.run --lang=cmn --audio=./samples/cmn/utt.wav --text=./samples/cmn/utt.txt --output=./samples/output/cmn
```

The outputs look like this

segments

```text
utt-00000-0000004-0000275 utt 0.04 2.75
utt-00001-0000275-0000509 utt 2.75 5.10
utt-00002-0000509-0000954 utt 5.10 9.54
utt-00003-0000954-0001173 utt 9.54 11.73
```

text

```text
utt-00000-0000004-0000275 有一个程序猿，他得到了一盏神灯
utt-00001-0000275-0000509 灯神答应实现他一个愿望
utt-00002-0000509-0000954 然后他向神灯许愿，希望在有生之年能写一个好项目
utt-00003-0000954-0001173 后来他得到了永生
```

### Japanese

There is also one Japanese sample in the `samples/jpn` directory. You can run the following command to align it.

```
python -m alqalign.run --lang=jpn --audio=./samples/jpn/utt.wav --text=./samples/jpn/utt.txt --output=./samples/output/jpn
```

The outputs look like this

segments

```text
utt-00000-0000026-0000185 utt 0.26 1.85
utt-00001-0000185-0000344 utt 1.85 3.44
utt-00002-0000344-0000616 utt 3.44 6.16
utt-00003-0000616-0001123 utt 6.16 11.23
```

text

```text
utt-00000-0000026-0000185 吾輩は猫である
utt-00001-0000185-0000344 名前はまだ無い
utt-00002-0000344-0000616 どこで生れたかとんと見当がつかぬ
utt-00003-0000616-0001123 何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している
```