module Test1(
    input [3:0]A,
    input [3:0]B,
    output reg C
);

always @ (*) begin
    C = ((A[0] & A[1]) | (A[2] ^ A[3])) ^ (((B[0] & B[1]) ^ B[2]) ^ B[3]);
end

endmodule
