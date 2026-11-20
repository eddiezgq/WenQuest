"""第 15、16 课的零件文件：从整机 STEP 做机架、上轴曲柄、连杆、针杆组件（model/slider/、model_en/slider/）。  LC_ALL=C.UTF-8 freecadcmd prep_slider.py"""
import FreeCAD as App, Part, os
D=os.environ["WQLS_TE"]; R=os.environ["WQ_REC"]
parts={"frame":(["bearing_front","nb_bushes"],"机架","Frame"),
       "crank_asm":(["shaft","crank","crank_pin"],"上轴曲柄","ShaftCrank"),
       "rod":(["rod"],"连杆","Rod"),
       "nb_asm":(["needle_bar","nb_link"],"针杆组件","NeedleBarAssy")}
for lang,sub in (("zh","model"),("en","model_en")):
    os.makedirs(f"{R}/{sub}/slider", exist_ok=True)
    for key,(files,zh,en) in parts.items():
        shapes=[Part.read(f"{D}/{f}.step") for f in files]
        if key=="crank_asm":   # 上轴只取靠曲柄的一段（到 x = 60）
            shapes[0]=shapes[0].common(Part.makeBox(33,40,40,App.Vector(27,-20,180)))
        s=shapes[0] if len(shapes)==1 else Part.makeCompound(shapes)
        name = zh if lang=="zh" else en
        doc=App.newDocument(en)
        o=doc.addObject("Part::Feature", en); o.Label=name; o.Shape=s
        doc.saveAs(f"{R}/{sub}/slider/{name}.FCStd"); App.closeDocument(doc.Name)
        print(lang,name,round(s.Volume,1),len(s.Solids))
