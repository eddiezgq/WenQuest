"""第 175 轮：问渠工作台的授权门。打包时各工作台的 InitGui.py 改成 `import wq_gate` 再 `if wq_gate.licensed(名称): 注册工作台`
（InitGui.py 可能在分开的 globals 里执行，函数放在这个模块里才可靠）。没有授权码或过期：弹窗让用户粘贴；还不行就不加载。"""
def licensed(name):
    try:
        import wq_license
    except Exception as e:  # noqa: BLE001
        print("WenQuest licence module missing:", e)
        return False
    st = wq_license.status()
    if st.get("ok"):
        left = st.get("days_left", 0)
        if left < 30:
            print("问渠软件测试授权还有 %d 天到期，请到下载页续期 / WenQuest beta licence expires in %d days" % (left, left))
        return True
    try:
        from PySide import QtGui
    except Exception:  # noqa: BLE001
        print("问渠软件需要测试授权码 / WenQuest licence required:", st.get("reason"))
        return False
    why = {"missing": "还没有授权码", "expired": "授权已到期", "signature": "授权码不对", "format": "授权码不对"}.get(st.get("reason"), "授权码不对")
    msg = ("%s：%s。\n登录问渠官网下载页，点“领取一年测试授权”，把授权码粘贴到下面。\n%s\n%s\n\n"
           "%s: licence %s. Sign in on the WenQuest download page, click “Get a one-year beta licence” and paste the code below."
           % (name, why, wq_license.DOWNLOAD["us"], wq_license.DOWNLOAD["cn"], name, st.get("reason")))
    for _ in range(3):
        text, ok = QtGui.QInputDialog.getText(None, "问渠软件授权 / WenQuest licence", msg)
        if not ok:
            break
        st = wq_license.save(str(text))
        if st.get("ok"):
            QtGui.QMessageBox.information(None, "问渠软件授权", "授权有效，还有 %d 天。\nLicence valid for %d more days." % (st["days_left"], st["days_left"]))
            return True
        msg = "授权码不对或已到期（%s），请重新粘贴。\nCode not valid (%s); paste again." % (st.get("reason"), st.get("reason"))
    print("没有有效的问渠测试授权，%s 这次不加载 / no valid licence; %s not loaded" % (name, name))
    return False
