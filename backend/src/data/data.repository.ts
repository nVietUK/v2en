import { DataSource, DeepPartial, FindOptionsWhere, Repository } from 'typeorm';
import { Data } from './data.entity';
import { Injectable } from '@nestjs/common';

@Injectable()
export class DataRepository extends Repository<Data> {
	constructor(private dataSource: DataSource) {
		super(Data, dataSource.createEntityManager());
	}

	async findAll(): Promise<Data[]> {
		return await this.dataSource.manager.find(Data);
	}

	async findOneBy(args: FindOptionsWhere<Data>): Promise<Data | null> {
		return await this.dataSource.manager.findOneBy(Data, args);
	}

	async createData(createDataInput: DeepPartial<Data>): Promise<Data> {
		const data = this.dataSource.manager.create(Data, createDataInput);
		return await this.save(data);
	}

	async removeData(arg: FindOptionsWhere<Data>): Promise<Data> {
		const data = await this.findOneBy(arg);
		await this.dataSource.manager.remove(Data, data);
		return new Data('', '', '', false);
	}
}
