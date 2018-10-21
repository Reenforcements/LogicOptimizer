module Test1(
    input [3:0]A,
    output reg C
);

always @ (*) begin
    C = A[0] | (A[1] | A[2] | A[3]);
end

endmodule
