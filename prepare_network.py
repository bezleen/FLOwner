import torch
from src.lenet5 import LeNet5
from bson.objectid import ObjectId


def export_network(net, file_path):
    assert file_path.endswith(".pt")
    net = torch.jit.script(net)
    torch.jit.save(net, file_path)
    return


def export_param(net, file_path):
    torch.save(net.state_dict(), file_path)
    return


if __name__ == "__main__":
    net_export_path = f"/Users/hienhuynhdang/Documents/UIT/kltn/FLOwner/storage/{ObjectId()}.pt"
    param_export_path = f"/Users/hienhuynhdang/Documents/UIT/kltn/FLOwner/storage/{ObjectId()}.pth"
    net = LeNet5()
    export_network(net, net_export_path)
    export_param(net, param_export_path)
