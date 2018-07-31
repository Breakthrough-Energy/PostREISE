function out = get_power_output_from_gen(file)
load(file)
%PG real power output (MW)
PG = 2;
n_intervals = size(mdo.flow,1);
n_generators = size(mdo.flow(1).mpc.gen,1);
out = zeros(n_generators,n_intervals);
for i = (1:n_intervals)
    out(:,i) = mdo.flow(i).mpc.gen(:,PG);
end

end 
