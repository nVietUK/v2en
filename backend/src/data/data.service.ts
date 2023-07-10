import { FindOptionsWhere, Repository } from 'typeorm';
import { Data } from './data.entity';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';

@Injectable()
export class DataService {
	constructor(
		@InjectRepository(Data)
		private dataSource: Repository<Data>,
	) {}

	async findAll(): Promise<Data[]> {
		return await this.dataSource.manager.find(Data);
	}

	async findOneBy(args: FindOptionsWhere<Data>): Promise<Data | null> {
		return await this.dataSource.manager.findOneBy(Data, args);
	}

	async createData(createDataInput: Data): Promise<Data> {
		const data = this.dataSource.manager.create(Data, createDataInput);
		return await this.dataSource.manager.save(Data, data);
	}

	async removeData(arg: FindOptionsWhere<Data>): Promise<void> {
		const data = await this.findOneBy(arg);
		await this.dataSource.manager.remove(Data, data);
	}

	async find(): Promise<Data[]> {
		return await this.dataSource.manager.find(Data);
	}
}
