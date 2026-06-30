Function Decode43(h39_VAFjx)
    Dim r40_CGZKMr, i41_HAYzLQ, p42_FzYLwwl, t43_paQbds
    r40_CGZKMr = ""
    t43_paQbds = ""
    For i41_HAYzLQ = 1 To Len(h39_VAFjx)
        t43_paQbds = t43_paQbds & Mid(h39_VAFjx, i41_HAYzLQ, 1)
        If Len(t43_paQbds) = 2 Then
            p42_FzYLwwl = CLng("&H" & t43_paQbds)
            r40_CGZKMr = r40_CGZKMr & Chr(p42_FzYLwwl)
            t43_paQbds = ""
        End If
    Next
    Decode43 = r40_CGZKMr
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode8(hexPayload)
'' WScript.Echo result
