Function Decode7(h2_AeQjx)
    Dim r3_wMtaoeOT, i4_tBpubmMy, s5_uWBftsVE, h6_turjFyEVkw, h7_JZIMybz
    r3_wMtaoeOT = ""
    For i4_tBpubmMy = 1 To Len(h2_AeQjx) Step 2
        h6_turjFyEVkw = Mid(h2_AeQjx, i4_tBpubmMy, 1)
        h7_JZIMybz = Mid(h2_AeQjx, i4_tBpubmMy + 1, 1)
        s5_uWBftsVE = CLng("&H" & h6_turjFyEVkw & h7_JZIMybz)
        r3_wMtaoeOT = r3_wMtaoeOT & Chr(s5_uWBftsVE)
    Next
    Decode7 = r3_wMtaoeOT
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode1(hexPayload)
'' WScript.Echo result
