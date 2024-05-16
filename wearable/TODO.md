# TODO

## Battery

Let's give [this](https://www.waveshare.com/ups-hat-c.htm) a shot.

## Bluetooth

One more thing to go wrong at startup, though?

## Slides

## Push to talk

This is how the
[AdaFruit people](https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/BrainCraft_Google_Assistant/gv_buttontotalk.py)
did it.

```python
dots = adafruit_dotstar.DotStar(
    board.D6,
    board.D5,
    3,
    auto_write=True,
    brightness=0.2,
    pixel_order=adafruit_dotstar.BGR,
)
```

Google has this whole
[`audio_helpers`](https://github.com/googlesamples/assistant-sdk-python/blob/master/google-assistant-sdk/googlesamples/assistant/grpc/audio_helpers.py)
thing with `sounddevice`.
