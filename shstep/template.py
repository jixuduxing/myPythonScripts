# -*- coding: UTF-8 -*-

import xml.dom.minidom

class itemtype:
    type_int32 = 0
    type_uint32 = 1
    type_int64 = 2
    type_uint64 = 3
    type_acsii = 4
    type_decimal = 5
    type_byteVector = 6
    type_else = 100

def toitemtype(strtype):
    if strtype == 'string':
        return itemtype.type_acsii
    elif strtype == 'int32':
        return itemtype.type_int32
    elif strtype == 'int64':
        return itemtype.type_int64
    elif strtype == 'uint32':
        return itemtype.type_uint32
    elif strtype == 'uint64':
        return itemtype.type_uint64
    elif strtype == 'decimal':
        return itemtype.type_decimal
    elif strtype == 'byteVector':
        return itemtype.type_byteVector
    else:
        return itemtype.type_else


class optype:
    op_no = 0  #   不占位  可选的用可空的表示方法进行编码，用NULL表示不存在
    op_copy = 1
    op_default = 2
    op_increment = 3  # op_copy   op_default   都占1位  可选的可以为空 NULl表示值不存在，此时除了default,前值状态也将设置为空
    #如果值在流中存在， 则成为新的前值  当值在流中不存在， 则根据前值的状态分为以下三种情况处理
    op_constant = 4  # 必要的  不占位   可选 占一位  如果该位被设置， 则值为指令上下文的初值
    op_delta = 5    #不占位，可选的可空，前值不被设为空， 而是保持不变
    op_tail = 6     #占位 可选的可空， 且前值被设置为空。

def tooptype(strtype):
    if strtype == 'copy':
        return optype.op_copy
    elif strtype == 'default':
        return optype.op_default
    elif strtype == 'constant':
        return optype.op_constant
    elif strtype == 'increment':
        return optype.op_increment
    elif strtype == 'delta':
        return optype.op_delta
    elif strtype == 'tail':
        return optype.op_tail
    else:
        return optype.op_no

#字段
class Field:
    def __init__(self):
        self.option = False #
        self.op = optype.op_no
        self.type = itemtype.type_int32 #
        self.prevalue = 0 #初值
        self.prevalueexist = False
        self.id = 0
        self.seq = 0
    #是否需要占位
    def needplace(self):
        if self.op in (optype.op_no,optype.op_delta):
            return False
        elif self.op in (optype.op_copy,optype.op_default,optype.op_increment,optype.op_tail):
            return True
        elif self.op == optype.op_constant:
            if self.option:
                return True
            else:
                return False

class message:
    def __init__(self,messageid,name):
        self.messageid = messageid
        self.msgname = name
        self.Fields = []
    def additem(self,item):
        item.seq = len(self.Fields)
        self.Fields.append(item)

class template:
    def __init__(self):
        self.messageitems = {}

    def load(self,filename):
        domt = xml.dom.minidom.parse(filename)
        rootnode = domt.documentElement
        templates = rootnode.getElementsByTagName('template')
        for templat in templates:
            id = templat.getAttribute('id')
            name = templat.getAttribute('name')
            print id,name
            nmesage = message(int(id),name)
            unknownexist = False
            # nmesage.messageid = id

            # result = [item for item in templat.childNodes if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE]
            for it in templat.childNodes:
                if it.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                    item = Field()
                    item.type = toitemtype(it.nodeName)
                    if item.type == itemtype.type_else:
                        unknownexist = True
                        break
                    item.id = it.getAttribute('id')
                    if it.hasAttribute('presence'):
                        presence = it.getAttribute('presence')
                        if presence =="optional":
                            item.option = True
                    if len( it.childNodes) == 1:
                        optype = it.childNodes[0].nodeName
                        item.op = tooptype(optype)
                        if it.childNodes[0].hasAttribute('value'):
                            item.prevalue = it.childNodes[0].getAttribute('value')
                            item.prevalueexist = True
                    nmesage.additem(item)
                    # print it,it.nodeName,it.nodeType
                    # break
            if not unknownexist:
                self.additem(nmesage)
            # break
        print filename,rootnode,domt


    def additem(self,item):
        self.messageitems[item.messageid] = item

    def getmessage(self,msgid):
        if self.messageitems.has_key(msgid):
            return True,self.messageitems[msgid]
        else:
            return False,1

if __name__ == '__main__':
    print 'template test'
    tem = template()
    tem.load('C:\Users\gao\PycharmProjects/test\shstep/template.xml')
