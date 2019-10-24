You can support the development on the gumroad page : https://gumroad.com/l/rVWY

"""

DOCUMENTATION

   Couture is a simple tool that eases the retology workflow for clothes.
   Import a piece of garment from scanned data, high poly model or marvelous designer.
   Garments must have uv unwrapped in order to process the workflow.
   Iterate quickly between 2D and 3D space.

   ### FEATURES ###

   - Outliner: Couture has a custom outliner that will make your work easier when you are looking for a specific piece of garment
   - Goz support: Thanks to zRemesher it's possible get a good base topo in few clicks. Couture allows you to quickly move from one software to another. Make sure that GOZ is already installed
   - CoutureNode: Couture creates a hidden node in your Dagobject outliner, this node will save every data needed by Couture, allowing the user to open a previous scene and restart his work instantly.
   However, if the user wants to start over in the same maya scene, this node must be deleted and the tool must be reloaded
   - Couture blendshapes: Couture automatically creates a blendshape between a pair of 2D and 3D piece of cloth. You can activate all blendshape at once or individually.
   - Couture wrap: Couture automatically creates a wrap between a pair of triangulated mesh and a retopologized one.
   - Couture edit: You can edit your geo in 3D or 2D space, this feature allows you to have a safety net in case you're not happy with your modifications.

   ### INSTALL ###

   Copy Couture's folder in your directory : C:\Users\UserName\Documents\maya\20XX-x64\scripts
   Use this code to launch Couture:

       import Couture.coutureUI as cUI
       reload(cUI)
       cUI.coutureInterface(dock=True)


   You can create a macro out of it, a custom shelf is also provided in the folder "Shelf"

   For more details, visit https://www.artstation.com/psichari/blog/z9b1/coutures-wiki

SPECIAL THANKS

   Remi Deletrain for his constant support and advices. Especially the Maya API side of Couture !
   My colleagues at EISKO,Cedric Guiard ,Gilles Gambier ,Pierre Lelievre And Romain Lopez  for their help on many different code related topics.
   Thanks to the people who were part of the Beta for their feedback.
   For all the comments, like and share from the community on the social medias, that was quite unexpected ! :)
   Big thanks to the people who created Qt.py https://github.com/mottosso/Qt.py
   Thanks to Ryan Roberts for his Wrap Deformer script


LICENSE

   See end of file for license information :  MIT License

Copyright (c) 2018 Florian Croquet

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
