# ALQAlign

under construction.

alqalign is a phoneme-based multilingual speech alignment toolkit. 

It is supposed to be able to handle ~8k language (at least theoretically). See the [full list](./doc/language.md) of supported languages. 

## Install

```bash
python setup.py install
```

## Usage

The basic usage with main configures is as follows, For the details of usage, check the [instruction page](./doc/instruction.md).


```bash
python -m alqalign.run  --lang   <your target language> 
                        --audio  <path to your audio file> 
                        --text   <path to your text file> 
                        --output <path to an output directory>
```

## Tutorial

There is one English sample in the `samples/eng` directory. It contains two files:

- `utt.wav`: a wav file containing 10 seconds of speech.
- `utt.txt`: a text file containing two lines as follows:

```text
A programmer walks to the butcher shop and buys a kilo of meat.
An hour later he comes back upset that the butcher shortchanged him by 24 grams.
```

To apply the alignment for each line, you can run the following command:

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