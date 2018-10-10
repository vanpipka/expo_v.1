import uuid
import base64
from PIL import Image

def savefile(base64data, src, resizeit=False):

    if base64data.find('base64') == -1:
        return ''
    if base64data.find('image/') == -1:
        return ''

    d = base64data.partition(",")
    print("Фото======================================================================")

    strOne = d[2]
    strOne = strOne.encode()

    #                 #print('=====================================')
    #                #print(strOne)
    #               #pad = len(strOne) % 4
    #              #print('=====================================')
    #             #print(pad)
    strOne = b"=" + strOne

    directory = 'C:/djangoprojects/main/static/main/media/'

    name      = src+'/'+str(uuid.uuid4())+'.png'

    with open(directory+name, "wb") as fh:
        fh.write(base64.decodebytes(strOne.strip()))

    if resizeit:
        resizeimage = scale_image(input_image_path=directory+name, output_image_path=directory+'/resize'+name)

    return name

def scale_image(input_image_path,
                output_image_path,
                width=150,
                height=150
                ):
    original_image = Image.open(input_image_path)
    w, h = original_image.size

    if w > h:
        position        = (w-h)/2
        croped_image    = original_image.crop((position, 0, w-position, h))
    elif h>w:
        position = (h-w) / 2
        croped_image = original_image.crop((0, position, w, h-position))
    else:
        croped_image = original_image

    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        # No width or height specified
        raise RuntimeError('Width or height required!')

    croped_image.thumbnail(max_size, Image.ANTIALIAS)
    croped_image.save(output_image_path)

    return output_image_path