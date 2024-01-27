using Chpack

fileName = "data/configuration_gen/elasticity/upload"
tmpfileName = fileName * "_w.txt" # 控制台输出
command2 = `awk '/Homogenized/, /Elapsed/' $tmpfileName`
command3 = `awk 'NR>1&&NR<8'`
mCName =  fileName * "_mC.out" # chfem_gpu 计算得到的6x6刚度矩阵
write(mCName, read(pipeline(command2, command3)))

mC=zeros(Float64, 6,6)
lin::Int8 = 1
for line in eachline(mCName; keep = false)
    global lin
    if !isempty(line)
        line = strip(line)
        print("$line\n")
        mC[lin, :] = parse.(Float64, split(line))
        lin += 1
    end
end

# RC = (m_C ./ maximum(m_C) .> 1e-3) .* m_C
# Chpack.ch3ep.computeProp(mC)

prop_output_file = fileName * "_prop_output.txt"
# write(prop_output_file, read(Chpack.ch3ep.computeProp(mC)))
open(prop_output_file, "w") do io
    redirect_stdout(io) do
        Chpack.ch3ep.computeProp(mC)
    end
end