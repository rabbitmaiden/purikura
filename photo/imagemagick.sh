convert chromakey.jpg \( chromakey.jpg -colorspace HSB -separate +channel \( -clone 0 -background none -fuzz 20% +transparent grey40 \) \( -clone 0 -background none -fuzz 40% -transparent grey60 \) \( -clone 0 -background none -fuzz 40% -transparent grey70 \) -delete 0,1,2 -alpha extract -morphology Smooth Square:3 -compose Multiply -composite -negate \) -compose CopyOpacity -composite out.png






