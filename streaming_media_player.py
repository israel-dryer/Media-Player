"""
    YouTube media streaming application
    Author:     Israel Dryer, israel.dryer@gmail.com
    Modified:   10/19/2019

    * idea for media player layout
        - https://www.sketchappsources.com/free-source/7-desktop-music-player.html
    
    * source of free icons and buttons
        - https://icons8.com/icon/pack/media-controls/ios-filled
    
    * Make sure the VLC install matches the Python version (32/64 bit)
        - pip install --upgrade youtube-dl
        - https://get.videolan.org/vlc/3.0.8/win64/vlc-3.0.8-win64.exe
"""

import PySimpleGUI as sg 
import pafy
import vlc
import requests
from PIL import Image
from io import BytesIO

theme = 'BrightColors'
sg.change_look_and_feel(theme)
bg_color = sg.LOOK_AND_FEEL_TABLE[theme]['BACKGROUND']

# ------ BUTTON IMAGES--------------------------------------------------------------------------- #
btn_ff = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAACk0lEQVRoge2ay2oUQRSGPwXtiBgMaBQUDOgmvoKIG0kYcBHERdRn8EKeQqMLRUHc+ghiNFmKLkLISkEnk8GF0YWCIATBOCG6OFMQi+quS1d3V4b88K+6zunzd9epOnWBXaSFPRF9jQAXgHPAWeA0MAoc7D//BXwDPgEfgLfAa+BnxBiCkQHXgQVgE/jryU3gFXCt76t2HABmgK8OwbryC3AbGKpLRAvoRhSgcxWYrFJABjysUIDOZ8ifj4pjwHKNIhSXkAEjCsaQ3123CMVOP4ZSOAq0GxSh2AWOh4oYopnuVNTNgoboJwkEr/ORr4hWAkHnccJVRAasJBBwHldxnDRnEgjWxls2ERlSKjQdqI1raIm/VxNyBThhU5sATgKXixos4PZFLgLvHNuWsSniXJ6IEdxLcYB9wA3gR4U2RewBwyYhUx5O9A9wB9iowMbGSyYh9wOFKIwDLyPb2DhrcjpXUohCXi6E2Nj43OSsE0kISC7c5P9ccLHxzZ+2yZGPA1dsz4UQG1sc300OfBLPF+OBNrb8+a0a6xPiQGBgupZPxWtDXcn+0eQo5vD7PpJN0PB7r6SQJibEuyanA1OiHGZnFY1/yCkaAeYdnbSQHXWfF4fYFPFFngiQXfFYL6qa00VCdtJSd//2wPWZfQMp51PHLJIjhchIY5s0jx08dhwnEwjYxC1k8vTC4wQC1/nAVwTI71tKIHjFRbQE98ER0siXLnLYVApj+C2DY3MFOFVWhMIozXSzReSwKSrUYehWTSKeUvHZ+wTVdrU2AUNsKDJka38tooDPSGXcyA2IDLiKrC57DsHq7CFV7DQlhlaIe6lmGLlUcx5Z+Z1BEvVQ//k6slnQRdbab5BLNesRY9hFMvgHseIuy/Q8Sy0AAAAASUVORK5CYII='
btn_pause = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAACYklEQVRoge2ay2oUQRSGPzXYCcZgoonuDHhBfQVjspGEvIGaZ5BIHkNcKAriVnwEg0TchEQIIevcZnBhdKEoBC8LkxBdnC4omu6e7q6aPtWSH36omR5q/m+qq6b7VMORwtIxj30NAhPATeAGcAkYAU7Fx38DX4APwDqwDCwCux4zVFYEzAALwAHwt6QPgDfAvbiv2tUHzAGfC4Qt6k/AA6C3LohpoO0RIOkWMNVNgAh40kWApF8iI+9V54G1GiGMV5EFw4tGkeGuG8J4O87gpGFgUxHCuA1cqArRi87plHeaVVqinwcQPumnZSGmAwid5cmiEBGwFUDgLLco+Kc5F0DYTp7tBBEhlwraQTt5hw4Tf6Zix2ny8dk8380DWWgQyHwWxCDVLsW1QPaBAdPBcauzCeBEFmWA6gHGzQsbZKz+LM5KBbmuEMRV10zDBrmiEMRVV03DBjmrEMRVQ6Zhg/QrBHFV6qrVaNkgv9RSVNcP07BBvikEcdV307BB2gpBXNUyDRtkXSGIqzZMwwZ5rxDEVUtpb56hWReNe2Qsv7vAu4wvClFvyVi1QMqUTdGrvINNutU9aQdPjsgf4FGh30NXD5E5kquIMMqkWd6mRMVxKoDAaT4EbheFMHoWQPCkH5eFABm+1QDCG6+QmOBldI4w5ksb2Wxy0igywbQgtoCLrhBGI+icZivIZpNXmc3Qw5ogXtDlvfdJunuqbVJhia2qCCnt73gE+AjcR+kJiAipis8jtdiy4feB18AdHJZW8PtQzQBSP76FVC0vIxP1dHz8J/AVWUo3kJuixfj9I/13+gddib3oMrgKWQAAAABJRU5ErkJggg=='
btn_pause_red = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAEJklEQVRoge2a3WscVRjGn3fOLOmanUCtaZpVwZJErVK8EAmajQkUokMbkVLvpLelttRCwT+iFISqKL20BS+KNiQmS1Mvtm66Enon2FI30YbWrkmbpmQ2pNvdmdeL7qyT3Z3NnpnNTgL9XZ2P98x5Hvbs+ZoBnrG5oEY9aG5/bHtIoQGy0AfCGwB3AdgJoLUYsgJgHqC/wLhBCqZWhbi6eyTxqBH9+zKS1vWWVrF8SIFymMH7AAjJR5ggXCHgvFHQfuyJx3NetXgycueTd8NiVRwl4BSAqNfOy4T8YzGfya2EvtudSDz20F6OzHCfDtBXYHTJtq0PmmHG8eh48rJUq3oDnw4j4zQBJ+TFeeJ8IWweefnib6v1BNdlZP6j3g7LCo0DeNuXNGnoOoXMA7supRbWjVwvIPPx4CsomFcA7m6MODkYSJOqDnWOJG7XiqtpJKP3t0NwEsBrjRQnDWFWmGps50TiX7cQxa3i78HBbRAcR9AmAIDRZSrmaFrXW9xCXI1si5hfoun/iVrwOxGRPeNWW3VoZYb7dDBNbJwo7zBZH0THUpPl5RVG0rreEhHG7wBebYoyaWjmcVbsLV80K4ZWqzCOYdOaAADuDkcKR8pL1/wiaV1v0YQxy8CLzRPmibtZU+t27s1UZ22rWD7EIGkTnT9PVQzRzIEY+42twUuaahwE8INdsGZoKVAOSz4wMJjpU2e+ZGRuf2x7cSu+ReChRb23zc6VjIQUGoD8eSJI1Lwaet/OlIwQOBaMHu8wc6URMO0JRI0v6HU7VTLC4J5gxPiitN45hhZ2BKPFF8/bCef0GwlAiF8qZ62tjtNINjAV3lm2E04jDwIQ4pdFO+EwQjNBKPFJ2k441hHcCESKP27aif/XEQXXgtHiHSIk7XTJSE6IBAAzCEGeIORDhfyvdrZkpHgr/ksgorwxuSM+XXXWAhG+b74eb5BFF9bknZmtdNR9GF7qevPiH0/sgjW/SE88nrOYXe+ONgvEdNppAqiyRVmx2r4FcKtpqiRhIG1YkXPl5RVGeuLxHDN93hxZ0rBgfFbtzVbVTWPxJcs3Gy5LEgbOdoxPVZ1ZXXe/WVM7BdD1jZMlCWF6Kbz0hXt1De4ND75AXJhC0DfyhFmF8n0do9PzbiE1zyPRscQDqOqH7NicBcCfbFr7apkA6jhYdY4kbishKxbIMCNMw6RYdCI1t15oXSfEXZdSC1kz0s/AWQCy15ueIMK5bEEb6Iwn79cVL9vBveH3hsDK1wRs1K3LLYVx3G12ckP6zB4dS02umNpeAk4CuCvbvgZ3iOlE1tTekjUBNOATDk01Dj69UOYhlN3u10EBhMtk0YXF5x7+VL7tkKFhH9Us6r1teREaYHA/QHsAdAPUDrBW7MoAeAHADICbREgK4qvto9eMRml4xmbiPyH5S8N8qXteAAAAAElFTkSuQmCC'
btn_play = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAFRElEQVRoge2aXWwUVRTH/2dmltIt7AoETZAHErZ8iC0tu0XE1sYQQdHEhPBiJPgGiqx0hSDGlzUx0UBhS1eC6SMQXww8GD/CR4JYRZAutFvB4C6mhpDIh4ZdaLfb3ZnjA90y+zG7Ox+75YHf05075557/pm59557Z4DHPFqQVY4awrtmYGy0nSC8APAzAOYDeBJA3bjJMICbAP4C6Aoz/yxKfKa/ueuuFf2bEuKKeGtq4+J6MG0kYBUAUacLGYyTTDiccKaPRuuDSaOxGBLy/Flf7cgUepehbAdojtHOc7gBos543PHl0Ev+Ub2NdQtpuNDxKhGCAM3X27bMgKIgZeuAe/9xne3KwxXx1thj0m4A7+uOzgiEw3VJbP51ZSBRnnkZPHtu21OCJHwHwG0qOJ0w0QWShNfDSztvlbItKaTpUsc8lukkAy5rwtNNRBB5dX9z11Axo6JCmi96Z8uK1AtgoZWR6YevyYqt9fLyPf9oWQhaN+ad9k+VFekHTLoIAKD5gih/44p4a7QsNIU4pscCqPKYKAYxt9TFpU7N+4UqH0yx9H3lwjIOAWsGPIETufV5T8QV8dYQUVd1wjLEgXmn/VNzK/OE1MVs7wFYUJWQDMCAyzE9tjm3PkuIK+KtYfAHhjthvMzAFaPtdbAjd+BnCamNi+sBPG3U+2BL4FTCmV5GwEcA7hv1UwZz7XfFdeqK7FeLaaPZHqL1weSAJ/C5KNgWgnAYAJv1WRCiDVmXmUJDeNcMGkvehv5UfIKwJ5A3CzaGfG1gdANoMupXg3RtOj3r/IpgHFA/kbHRdpgQoUXYHegNu51uML0N4LaFrqVRm+3FzMWEEAK1WthJNuRXwi37DsljWATwQQCyFW5Z4XwhABZb4bwYl1cG/gt7urYICnsA9FrgclGmoBZSb4Hjsuhf3tUfdgfaGXgLwA3DjujheqcWMstEbEaC4EFP4CsbhheA6RMAure3AGZmCmoh00wHZ4CQp2ck3LLPLxMaCPhaZ3NHpqCZ/U4GDNQabSupyvehelTVwt23yZ7iaTvB/CGAvGSwBPFMQS3kDqophEENId+bKWA3iI2mRf9mCmohUVQp6236raNJCVE3gDZTjhiRTFElhK4AvNaU4xIsOeubKU7hTxXQJliQRZBAf2TKE0IYyi8E2mHWeUHYLzT2xTeAuBOg2RZ6nlhUJ4SIIn5UZMiwON9qDPnaEIp1gyxPGlNTU6mfMhcT0++DU3E6ZVUvzRd3zmkM+Q6BcQbWZ75g4EQm8wWyBzsYfIiANWY6cEW8NXUxyScrqY9RwUWWGEfU11kLYsKZPgoTuU9TX8dr9pg0yMBnqGymcF22O4+pK7KEROuDSRBpnh2VQgF9iyoknwTec3mJf0xdl5eijDhSBwFcrXQwJogMO+We3Mo8IdH6YJJI2VadmHTDzNhS6MtWwaRxwL3/ODEdqHxcuukebAkUnFk1s9/hJ1LbmehC5WLSzXm51rlT66amkGh9MDmFaS0eifHC15S08kbuAFdTdD8S8uy9I4j8CvAwOZsE/hQFcdXvK/bfLGZUcmPV39w1BJvYOkmv2XlRSLdeWrb371KGZe0Qw0s7byUcqTYA3ajUyWEOxOgZcabbLy0LlnUWpvvz9NI+32oGvkDlFr6rzNiqNTtpYeiHgfFP1e8A2AFgrhEfBbhO4D3DTrnHyB8Qpn/hsN8V140fKK9GThJaBmkGjhPjiGx3His2K5XCsp9qnjvndSRsUjsUtIGwGA8+Z88GMH3c5B6AW2BEx3d2vaMJ6czV1t33rIrhMY8S/wNbdKPkpZLOBwAAAABJRU5ErkJggg=='
btn_repeat_off = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAABbklEQVRoge2ZQW6DMBBFX3ud5gaE9hKtsmjvEambZtnjtLkTp2gQXQQr1CHBzNjGqeZJXkQy9n8MQTCAYRil8rB0gBi8AD/A59JBNDiJrh83KbPhr0TX/14tGWoufiU64AC85gpQA3ug8UKEDMdYJUJG0+9dayXegVYQYCgilRiOts8iolJKOJHnCCJO5kki8h1hc0eMqnR9ptn4/4lKssiAscocgLcrx6y9+Y1k40tnV4Pk9qvOkUIEzivzkTpHKhE4yUxJRMmRUgTCHxqDctxNLBA6NyVBOe4zBMmCiZSGiZSGiZSGiZSGiZSGiZRGbJEi+7lz30d2TL+D58ihWmA3mBdbJpvIivGGwkayqSLHRfx20PrKXEmrJ4Qo7aA952dj7vAro13vSyJScTyrMWU067TAo0QE9E1sd4m5TwcaCXET21Fz7LlKPitoL62m31tcibks/hEnBqlvv1nZcsOV8NnyDyQcRT40GoYBv+3dlI8pg9BtAAAAAElFTkSuQmCC'
btn_repeat_on = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAACw0lEQVRoge2Zv07bUBSHvxPSqX8eBNWmhFgVHdmo2KBSg1SewTFDK7UqacXQDgl5hXYgA3Sqijq0K62wCcWReJDSDZLTAYoSFLtxfEky+Nuuff3z/XTt66tjyMjImEhmm+vTJvNyJsMGxfa95Xan82smKL8zlSmmggbF9r1lRBvArcsBvD8ubr1ImztSEdt3VxBpAPmuw+dTudzMUaF6kiZ7ZI/WxUzINr0SbVTX0krAADMyc+gtqWoZeAjcThIeFrcEwAq8J4JelxiEP8CBqlRbTm0vrmPsjNiH7qaqfgYWSChxleG7pSElAO4ACyL6xQrKb+I6RorMHHpLqLwc4uY3gsBry3cXo85HiqiqZ2IAoVNvKLIKnKfNEmQ96lzcdBd7U2Q+nKv9HGYArWJtx/Zd7bdioVoKnfpuv+uspjsvHdn/11bBibpH3Dtyt7sxrMTV9U59F9USvTOTR6QR9ZVvFeo/utsC96LyR/plv5CRp8DZ1UHRTRPL78i3KKFT+4RKCThDtBLO1WNXo0EZy14rdGqfpnK5B6YkYEwiACYep27GJmKaTGTSyEQmjUxk0shEJo1MZNLIRCYNoyKm67lJMCZi+16l3emEVlBeNZWZBCMitu9VEN0ApgQ+jkMmtchsc30a0e7615TAB9t3V9JmJyFO5LS7YTXd+X6djgrVk6jqSFqZ+wfeo+62wu+ovnF1LZ+LUikA0pF9OygnGUcekYYVeNIq1nYA7KCsSQKgt7sIB1E9YyqNUk12077kBd22fbdkIAsgckyRIi2ntqfw1tAA0iNaCee2vkadjn3ZW8WtDVV9jPKda+/MgJwrsho69cYQ1wKcInxDWPxf6cjIH6vrv9MuaaP6LIVEIlKLzDbXp9udzjEJitM3QervyFGheqLIq65DbVTXRilhFCvwnttB+dzgCjU+xrlpzMjIiOcvMWjzvTtdjCkAAAAASUVORK5CYII='
btn_rewind = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAACk0lEQVRoge2azWoUQRSFPwXtiBgMaCIoGNCNvoKIG0kIZBFEIeoz+EPewuhCUZBsfQQxmixFFyG4jjOTwYXRhcKAEATjhOjidsFQVHdXVVd3V4YcOKueU5wzfav6VnXDAeLCoYBjjQHXgCvAZeACMA4cT6//Bn4AX4AN4CPwHvgV0IM3EuAusArsAv8cuQu8A+6kY9WOY8AC8N3CrC2/AQ+BkbpCzADdgAF0bgLTVQZIgGcVBtD5CrnzQTEBfKoxhOI6smAEwSRyu+sOodhJPZTCaaDVYAjFLnDGN8QIzZRTXpl5LdEvIzCv87lriJkITGdxyjZEArQjMJzFTSwfmgsRmC3ig6IQCdIqNG20iFtoE/+wFuQmcLYobQQ4B9zI+8Eq4f61NjBboWY5K8QYfq24zh5wDziSjluVpg+MmoLMlQzQB5aQbmAQoTWDnDUFeVIixFvgkmnQwBqdiybxskcAVdN5CKHJ4muTuOMwgF7TNqZ6wH1HTRFbJnHPQphV03nw0dgG+WkS7xSI8mo6Dz4a2yB/lEB/IA4Fhqa0XDreWCb7Z5PYd/m95WjKR+O0/D72CGKzEITU6HxkEg9Ni3KS/dU0/iWjaQRYCRBEcQP3vb+L5k1WCJBT8VBBquZ8XpD9tNU9Omhcf7LvIO187FhE5kguEuI4Js1iB4cTx+kIDJu4B1y3DaHwIgLjOp+6hgC5fesRmFdcQ5vgLjhFHPOli7xsKoVJ3LbBodkGzpcNoTBOM2W2hts+xgrqZeheTSGWqPjd+xTVlloLjyXWFwlytL8VMMBXpANu5AuIBLiN7C77FmZ19pEudp4SSyuE/ahmFPmo5iqy87uITNQT6fVt5LCgi+y1PyAf1WwH9HCAaPAfEeAv7UbpySIAAAAASUVORK5CYII='
btn_shuffle_off = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAACf0lEQVRoge2avU8UQRjGf4c5iI2htLEw5kIihPiRWFgpYEPoPEGD2Mm/AOX1tKIVpWiHnQEbCIVGqKTBr9ZQEguVU1mLHXIzsx83swz3cmafZHN7875553luZnZnnhyUKFGiGzEoTSAEGsAf4KEwj2OhAUTq6loxQ8BvWkIi9X1KklRR1EmKCTYyUcZ1AHwEngK1AnVrwDNVo5nTT7CRyetAFzXjUXMS+OFYO5gY144OgTsO9UZVro+Ioyk23QkhEfAZqObUqgJfCog40UVfBR6QnN95U+yRldsE7tMSf4/0xX6skXDFotXxB6CSklcBdqzcJ1pc/PF7MYXAeEreBMlf+pKVM4fASOhYxiS5kZKzaeU8z6g1h5AIgGGST6KbWvyGFYuAqzn1RDeNq5hEV7TYKyv2uuPsPDBC8r1yGegH/lqxESGOzniLSXhJta9pbe9lqPmhTvI9cQEY09ruirHzQA/wCVPMgoptE7/Vz8hQ88csppDvxOtkEngsyMsbfcA3TDHzxCPRJ8irEOYxhewBZ0UZFcQ5YB9TzKwoowLoUZ8LmEK+0kULHeKt+BhwHviJKaYuyMsb74A36n4JU8iWFClfjNIifR0YoAu3J2BuRV6qthVMIasy1NxxheTBqZ/0Lfy1NrVEt/EvMMmua7ENK7acU6eBoF3a7rg7TnK07GMunALvt50BUVFtes6iVUPUfOglPlu7WEIzVk6T2E7q1XJEvN+sK8ukq6qYb71gI+PT4SFwK6fWbYrZpUHEuHb0CzcLp46/gX00xU7M+z0Adokdw7SnUBZqxIt9V9XoyNTqJES931AQ935DQtz7DQlR7zc0/os/DJQocZrwD3gNuSdUVZxuAAAAAElFTkSuQmCC'
btn_shuffle_on = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAFIklEQVRoge1aX2xTVRz+frel4gNgfNAXNMYwJRu9Zd2taELCiC4x+mCi48+mzBf8swdd24EQNbGPjmVtF5wS9AWMTAWJPqnoBI0Pwm07e+uWgQRJ8IEHEQcKMnrPz4et7Nyy27XraRzJvrfznd+f8/Wce+45v1tgAQtYwC2Hxkx3faU+Wi0GUg10MxqzhbD8qUh7JX5UqwHNBboZjYH4rammzUBHzkgcKMd33ghpzHTX20JkAXglOg/mNiuUPDSb/7xZWsPBvlEwbQZwXaK9IPq4nGU264zoqQi7dE0AOAvwkE0UH2lKnC5rxFNoSEdWeJijAD0K4D4AvhLmeQa154z4QTeDambEB+ABgDo9jF8C6ehz5Tr6U9ENHoYFUOdkjJIiAMBL4MGAGd7iZqBqad3GzPv9JyLrZjNcbYabCfwJgNsrzMEM5N06VT4jRBrebz4a87oZNB+NeQXRXlS+yeQZ1G6FkoNuBq5JC7CMxIxJG0ZiPu3qeCsB+6Q4dReW/rUJwEcz+VxcemkzGHXOAeJ5H/45mDb2XtfNcCuIBjHDzpULJUruXFVvv3oq8h6Al6WA2WxTohEE5ybBID0dyQLwS+wey0h0AvNg+2VGL6S1y0DAnwo/XmwXyESfhFOEbRP6Co3hYN8og96U+8HcUY4IQIGQXChxBsyfyRxptKPYjlk4OcLB4i07Z8R7GLQTkyK2lHomiqHmYSfscrQZ6/RU15pCM5DqXgvQWoeLIKfPFHJGvMejaXolIgBFQiwjmSHwNzLH0G7MgIDY6fSgr7Oh+LBbvOFg32ilY5h11yoXrGk9ENxSaBPwlG52PTgh8n8Q8ITDmMSMs1ENlL1HrGB8CMBxR2zSto+tGbgAwlCBZCLTakp+pyrvdDKFYFBfEdWx6kT0HhbomU4o3laZczquQqw8c+4wgF8lapFG/EoulPgWjBSAU9ngHZ+rzFmA8vtIwIy+xMR7JOqy5uF7bVtrIYhllpH8QHVOoAb3kfG/l+4DcF6ilghb61x55tzhK8vsD1XnK0C5kLPrY/8S0O9kuev35ct9p+t2X1Odr4Ca3BAX5/PvAhiXqLuvLKKOWuQqQL0QjmnHH959CYy9Dp5424ZPN3iU5yuEVx0wkI5uAvPFvPBaHi3/G4DFhT4GbSx1Xa0GymeEmbczsGPkod7zKLqXEPh1cG0qN0qDrjK7WzQSRyYj0yMQ9kWQNgr5B9PosalTgFIonREN8lGdt1mh/pMMfCHbkBA3HfFVQNmM6KlwEKC0RIkJe+Iun8e7AtB+clpzk2UkM26xGjPd9ZWegJXNCE1eiKbB9OPYmoELltF/HITvnX14zS3OXGu/SoT4zcj9DDwtc4zpgyIL7nE4ELWuHn61DkWQar8eAvZXIkaJECJsByC/I3I5I/7ljYaR/IqArNTvEbYnKsdozHTXg/gN2YaAfboZbi1nDFUJaRiJ+aaqf1tlnoh2OaooBBbEvUXuW/3p8LMNIzEfUKj9chucRTgviAbLEVNN7dcNp+68vKzh2PqYoyrYfDTm/XPJ+CiAm5ZUGahp7XcmCNbEC8UiAODY+lheY34RQKU/DDBZ+z2gm+E2NwOVQq4xsCUX7P/BzeDnUPIYmDcCuDqH+EQlagzVCpkAMEaEd5hRX87XJSuUPCTg9RPTAICTUzFmQ55BbdlQ0vU+M2++WAGAbkafAfEggEUSXVaxbt4I+d9rv6pQbe133sGfiu7QU5F8qR3qlsFc/jCwgAUsoDT+AyEDAY/8TuOhAAAAAElFTkSuQmCC'
btn_sound_off = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAD6ElEQVRoge2aSYwNQRjHfzNvRowtlkSMNTg4yAguQojlIERISAhOSBycRCLiZC7WiAyxXTghiOUiYouD2CUkwyS2CSMYa2wziV071Fd5paf6vequ7jck/kkn79X/q+rvl66urqpugK3AU6CGf1jlQAegP3CefxwmBxwEAuA1MKJ90/FT2jBlwArgLvAe2A1UebbprLRgKoEj0o55bEohR2f5wlQCx2kLEQAP00vTTUlhKoFj2CEC4GeMHKqAcUBFjDpWxYUpBqEPVy2V+HpgfJzEbXKFcYWIA1IDvJU6v4Adcp7EKgZT6J7wAQHoAWwDfkjdS0CfJBBaUTBxIeKCaE0AXpIfMKoTtgO0hRmNe3fyBQEYBDSQv296erT1B8yXAskmBdkLHJakbeoN3JN2zqAeuomVA84lhCgEkgOeS0wrsDgibjDwTuJWJIXoLEcOdeOlfUUGACeM2I0RcXPJ94ohSUBOARc8YVy0HPXwDIA1ETG6i+8zCzsCdcCLIifX/02YyxmAACwz6syx+EOBbyjg4bqwzvHkZllSmDjaLnVeop4pYe0Rv04XRF2JQiBhmCsxQboBG4AlQKcIkCrgvtRba/HHGqAVtgRdQZLAhJMIUMvsyREw8yTmk5zHVBnQKP4kX5AwzFXHtnSSGv4bMM0CUg40ScxCi79TvNVpgMSBCasM1W0C4A3QyxKzUfwDFm+ReMfTAgnDXHME0Totfq3FmyHeA4s3Urw7aYK4wERpivi3LN4A8X6gupqpfuI1pw0ShrnuCNJT/FaLV2XUDw/D2vuSBUiAeup3tcBELc76it9SBKR7hNeaFUj4ytyQsqiV5mzxb1q8/kR3rWrxnmcJ4gpTLgAB9rnVdPHuWbxR4tVnDRKGCa80K1DDqi6zDb/rxC80/O4vBUgUTAvwTH5/BaZaEi1DLW8DYL7F1/OxlaUC0TAIzCmj/AUw0ZIkwCyJeQ90sUA2iT8K1BhcChCzLXMG8Ab7ANABuC0xtknjGPEe6YIt7QCiYQptNempSTNth11Q98UfkB0FJurKZAVSCGYxamPuFzDTUm8I8B34TIK9riTbP8VAbDCbyS91ayPq6LX9rrgQEG9rNA6IhjkUil0fEbtA/Fd47G/5whRSDrgocZ+wDwA14gUC5CUfmGLKkX9JFB4ABgKPxdvhC6GVFMZFtgFgGPBEys7huTMfVhIYV5kwH4EP8vskGb2LjAsTRzngrFH3KOohmZmyeNGj5bIESFVmV0gTJNx2SWCKXZnPHm3/VTANnm23C4ztg4FVKbRdcphy1O5fI2qavpUU3pmL/n8787fKvB9ft3Mu3qpEbUo0/Qb4AauIp3fTqgAAAABJRU5ErkJggg=='
btn_sound_on = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAADqklEQVRoge2ZSWgUQRSGv8lkJhMR3BXNctGLiiiCoCDGiIoHI0ZvggdxAUU0HnLwYBCNohDFLehFQQ9RcI1CvEQPHuOCG2I0LgHFnSi4RCdJe6hXzmRS3TPdPZmOkB+aHup/Vf2+qe7qqmoY1KD+K4WAKqAd+AwcAWKBZuRBEeACYKUcu4NMyq0iwCX6QljA0wDzcqUocBkzhAXEXbZXnNXsMlQEZwgL6HbR3hqpcxOYmtVMHZSuJ7yAzAI+Sr0/wC4gL3sp91WmEG5BAIYDh1G3pAVcB0ZmJesUuYHwAqI1H/ggbTwCRvtJOlVR4AqZQ/gBAShBQVjAXVRv+ZYXiHQgIWmzAZhgEzMWeELiNgsFAZEOJEri4f4GrLSJKwU+SVyVH4hGjxCZ3FpFJF6mPUC1TVyF+J3AJLvGRqQcen4UBa75gHDzjGwDuqTORpuYk+KfTS4cAtQDHYaLr5CYfT4h3D7sq1H/ehyYY/CLgJ8SM0MX1jtcfJzEPM8xCMB+qfcMKDD4B8Q/oQtMPaGPfImJO8R4AYkBO4BVNkmCup31kLvZ4E8W7ytQSJqLh6VSV5o4tyBlSeWvgHk2MBUS0455itIifkVQICFgHfBAvN/AYhuYVokpN3i14u0JCkQrjJpPWaj3yCiHZOsMnu6x5qBBQPVOs8TUGPwl4t0yeCXivRkIIAALJeaewSsW763Bi4n3a6CADJWY7+mSNegHYPXrYiVL0jn22Pih5KCgNVvOrQZPDwAdBi+Geod0DgSQELBdfjca/GlybjN4Y+T8JWiQMHAIWICantcbYubKucXgzZTzEwjmYQ8Ba+n9QlxkSDQEvJCYMoO/V7zaoEDKkspfkvjXU1UpMa8xP893xF8KwU0aa1CTxqgNRAHwWOpuMvhTxPs3aTzmcHE9jW/LMkgmqpN6rTawB8U/rgsKgaOYe6ZSYnK9sNogdeIkhuZkFaMWVt3AdFMDTkvdqzkCqZbYHmC9TcwpabMhwzZ7ye2GnFuQYhJ/Vjdq7W7SMhKbDxO9gEBmm9VeQPKA9xLXASy3iStFfTiygK1eIbS8wqTrkTPAaWC8jZ+8QdeEzw06LacPOtkatZKVvGV6Gxjmo60+cgvjFaScxC7kQ8yrSN+KABfpHxD9WUHPKppQI2m/KYwaBrMJkvqhZyc5WnJkAuPl09sN1FQkp4oA57EHMS1jnRTIx1AtJ5j7AeblSfnAOfqCbAkyKa/KQ82ZWoF3qAVQ2LHGoAY1MPUXSJoQk5K4syMAAAAASUVORK5CYII='
btn_stop = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAACbUlEQVRoge2ay2oUQRiFP43YCWowaqKgYMAL6it4yUYSshUXXp5BlDyGuFAUxK34CIpE3AQVQnCd2wxZGF0oCsHLQidEF38XFMX0THdVTf81kg8O1HQPNed0Xaa7qmGbtNgRsa4RYAI4D5wDTgBjwJ78/C/gM7AGLAJvgTlgI6IHbzLgJjALbAJ/K2oTeAncyOuqnSFgBvhUwmxZfQTuAIN1hZgGmhEDuGoAU70MkAEPehjA1VOk5aNyGHhfYwijBWTCiMI40tx1hzBazT0EMQosK4YwagJHfEMMotOdOnUzryn6cQLmXT2sGmI6AdNFmiwbIgNWEjBcpAYl/zRnEjDbTbe7hciQWwVto920jjPwdzpBrgJHu6VNgGPAlU5fmMXvCoXi85sviiobwe9WXCtICxg2FdhdawIYiGCqLnYBl8wHO8iF+r0E0zbIWQUjoZwxBTvIKQUjoZw2BTvIQQUjoRwwBTvIXgUjobSdtfoaO8hPNRf+fDcFO8hXBSOhfDMFO0hTwUgoDVOwgywqGAllyRTsIO8UjITypt3B/fTXTeMfCqbfDeB1BFN18YqCWQtkmdKH0Cc+H551OtlPj7q7beNui/wG7pW6HrrcRcZIRzLSWCYt0ioVVhynEjDcTlvA5bIhDI8SMO7qftUQIM23kIB5o3mcAV6FQ6QxXprIZlMQ48gA0wqxAhwPDWEYQ6ebzSObTVExm6FbNYV4Qo/33ifpbVdbxmOK9SVDlvbXIwb4ANxC6Q2IDLiOLCi3Sph11QKeA9cImFoh7ks1w8j68UVk1fIkMlD35ed/AF+QqXQJeSiay49v89/xD7AqnDUpCEYUAAAAAElFTkSuQmCC'

# ------ VLC PLAYER ----------------------------------------------------------------------------- #
# get video
url = 'https://www.youtube.com/watch?v=YR5ApYxkU-U'
video = pafy.new(url)

# meta data
title = video.title 
channel = video.author 
category = video.category

# thumbnail - convert to png format
img = Image.open(BytesIO(requests.get(video._bigthumbhd).content))
with BytesIO() as output:
    img.save(output, format='PNG')
    thumb = output.getvalue()

# retrieve audio url
audio = video.getbestaudio()
playurl = audio.url 

# media player setup
Instance = vlc.Instance()
player = Instance.media_player_new()
Media = Instance.media_new(playurl)
Media.get_mrl()
player.set_media(Media)

# function flags
pause = True
repeat = False
shuffle = False
sound = False

# ------ GUI LAYOUT ----------------------------------------------------------------------------- #
btn_format = {'border_width': 0, 'button_color': ('white', bg_color)}
rc_menu = ['&Right', ['!&Playlist', '&Minimize', '!M&aximize','&Exit']]

col1 = [[sg.Image(data=thumb, pad=(0, 20))]] # album art
col2 = [[sg.Text(channel, font=(sg.DEFAULT_FONT, 26, 'bold'), pad=((10, 5), (40, 5)), size=(16, 1), key='ARTIST')],
        [sg.Text(title, font=(sg.DEFAULT_FONT, 12, 'bold'), pad=(10, 5), key='ALBUM')],
        [sg.Text(category, font=(sg.DEFAULT_FONT, 12), pad=((10, 5), (5, 40)), key='SONG')],
        [sg.Button(image_data=btn_rewind, **btn_format, key='REWIND'), 
         sg.Button(image_data=btn_play, **btn_format, key='PLAY'), 
         sg.Button(image_data=btn_ff, **btn_format, key='FF'),
         sg.Button(image_data=btn_repeat_off, **btn_format, key='REPEAT'), 
         sg.Button(image_data=btn_shuffle_off, **btn_format, key='SHUFFLE'), 
         sg.Button(image_data=btn_sound_on, **btn_format, key='SOUND')], 
        [sg.ProgressBar(max_value=100, pad=((0, 0), (38, 0)), style='winnative', size=(32, 35), bar_color=('#F95650', '#D8D8D8'), key='TIME')]]

player_layout = [[sg.Column(col1, justification='left', key='LEFT'), sg.Column(col2, key='RIGHT')]]

window = sg.Window('Music Player', player_layout, no_titlebar=False, grab_anywhere=True, keep_on_top=True, right_click_menu=rc_menu, finalize=True)

# ------ EVENT LOOP ----------------------------------------------------------------------------- #
while True:
    event, values = window.read(timeout=100)
    if event in (None, 'Exit'):
        break
    if event == 'PLAY':
        if pause:
            pause = False
            window['PLAY'].update(image_data=btn_pause_red)
            window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())
            player.play()
        else:
            pause = True 
            window['PLAY'].update(image_data=btn_play)
            window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())
            player.pause()
    if event == 'SOUND':
        if sound:
            sound = False
            window['SOUND'].update(image_data=btn_sound_on)
        else:
            sound = True 
            window['SOUND'].update(image_data=btn_sound_off)
    if event == 'REPEAT':
        if repeat:
            repeat = False
            window['REPEAT'].update(image_data=btn_repeat_off)
        else:
            repeat = True 
            window['REPEAT'].update(image_data=btn_repeat_on)    
    if event == 'SHUFFLE':
        if shuffle:
            shuffle = False
            window['SHUFFLE'].update(image_data=btn_shuffle_off)
        else:
            shuffle = True 
            window['SHUFFLE'].update(image_data=btn_shuffle_on)
    if event == 'REWIND':
        pos = player.get_position()
        player.set_position(max(0, pos - 0.01))
    if event == 'FF':
        pos = player.get_position()
        player.set_position(min(1, pos + 0.01))
    if event == 'Minimize':
        window.minimize()
    if event == 'Maximize':
        window.maximize()    
    else:
        window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())