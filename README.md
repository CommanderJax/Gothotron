# Gothotron

Gothotron aims to facilitate using Tacotron2 and other state-of-art speech synthesis models to replicate the original NPC voices from all Gothic video games. The primary goal is to outline in an approachable way what is required to start working on speech synthesis with Gothic voiceover data and make it available to people with limited ML experience. The secondary objective is to create an end-to-end data-generation pipeline that can be immediately fed to other speech synthesis architectures in order to gradually improve the quality of generated voices over time.

The author hopes that his effort will ultimately result in engaging and motivating the Gothic modding community to incorporate artifically generated voices in their work and give the Gothic fanbase a unique breath of freshness. 

##  WARNING

This project is in a very early stage of its lifetime and is not ready for use without prior experience with Tacotron2 and, of course, basic fluency in python.

The only reason why it has been published already is because numerous people have requested a tutorial on how to work with Tacotron2 on Gothic datasets.

## Requirements

1. Machine with a modern GPU or access to remote environments with a GPU(for example, Google Colab). 
2. Coding experience. You don't necessarily need to know much about Machine Learning, but you absolutely need to know how to code if you want to experiment with this tech.
3. Gothic/Gothic2 and some mod tooling to retrieve the audio files [here](https://www.worldofgothic.de/dl/download_104.htm)

## Audio samples

[Nameless hero, 3 hours of fine-tuning](https://soundcloud.com/victori-w/sets/gothic-nameless-hero-reads-famous-quotes-ai-trained-model)

## Getting started

1. First and foremost, go to [tacotron2](https://github.com/NVIDIA/tacotron2) and try to make it work on your machine.

    Unfortunately the repo appears to be unmaintained and it might take a few hours to resolve all the issues. 
Their code is also a little bit of a mess, the dependencies were not pinned and neither the Dockerfile, nor the requirements.txt will work out of the box.
Ultimately we will likely fork that repo and fix these issues, for now you have to experiment on your own.
If you plan on using Docker, the official [NVidia Pytorch image](nvcr.io/nvidia/pytorch:20.08-py3) is a good baseline to start from.

2. Instead of using Tacotron2 scripts you can use a notebook (check the notebooks directory in this repo). 
   The only thing that we will change in tacotron2 for the time being is the training/validation datasets and filelists.

3. Once you've managed to run Tacotron2 on your machine you need to prepare the audio training and validation datasets. The bulk of work has already been done in this repo.
   We need to do a couple of things here, firstly, extract the audio files. You can do it with GothicVDFS which you can download from [here](https://worldofplayers.de)
   Once you're done, save them all to a directory on your filesystem, let's say `gothic_wavs/`.
   
   Now, you've got all the audio files in a single location, great. We now need to figure out which audio files represent dialogues spoken by a given character.
   The easy way is to just copy the pregenerated filelists from the output/english/CHARACTER_OF_INTEREST/ directory. 
   Be warned, I haven't tested what is the minimum dataset size to generate satisfactory results, 
   but many characters most definitely have too few audio samples to produce decent quality models. You can start with the nameless hero who has a little over an hour of dialogues.
   Generally, there were voice actors that supplied their voices to multiple characters, but I haven't figured out a way to associate actors with characters yet(I couldn't find these mappings in the game files).
   
   If you want to generate the datasets yourself(you might want to do that because you'd like to create a dataset for different language(e.g. German) or because the datasets are randomised and subsequent generations will product different files which are likely to yield different end results), clone this repo and run:
   `python main.py -o PATH_TO_YOUR_GOTHIC_GAME_DIR\_work\DATA\scripts\_compiled\OUINFO.INF`
   Be warned, at this time the code doesn't really support other languages that english, however if you have German or Polish files it should still work.
   
   There is one more step that needs to be taken before starting the training. We need to downsample the audio files(I will explain why this is necessary as I get more time to work on this project).
   The easiest way is to use ffmpeg, there are other options, but if you want to ascertain that you'll do this correctly, just use ffmpeg:
    ```
   for i in *.wav;
      do name=`echo "$i" | cut -d'.' -f1`
      ffmpeg -i "${name}.wav" -vn -ar 22050 -ac 1 "downsampled/${name}.wav"
   done 
    ```
   You have to run it from the same folder where your wavs currently reside. 
   If you're on Windows, you're out of luck. You either have to rewrite this code into powershell or figure out another solution.
   
4. OK. At this point we're ready to start training. Copy the generated filelists into `tacotron2/filelists` and move the content of `downsampled/` to `tacotron2/wavs/`.
   And run all the steps in `notebooks/tacotron2/tacotron2.ipynb`.

5. This is a very rough tutorial released prematurely just to get people started, many of the above steps will require some experimentation. The end goal is to remove all this burden completely, but a tonne of work lies ahead of us before that can happen.

## Sources
[Tacotron2 code](https://github.com/NVIDIA/tacotron2)